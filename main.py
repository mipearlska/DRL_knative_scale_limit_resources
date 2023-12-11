import schedule
import time
import math
import os
from configs import configs
import requests
import csv
import rolling_update
from kubernetes import client, config
import numpy as np
import environment
from sb3_contrib import TRPO

global state 
state = np.array([1, 1, 19, 1, 1, 15, 1, 1, 33], dtype=int)

def get_traffic_metric(generatorIP, generatorName, serviceName):
    #q = 'rate(nginx_ingress_nginx_http_requests_total{app="nginx-ingress", class="nginx"}[15s])'
    #q = 'sum(rate(nginx_ingress_nginx_http_requests_total{app="nginx-ingress", class="nginx"}[15s]))'
    q = 'locust_users{instance="' + generatorIP + ':9646", job="' + generatorName + '"}'
    test = []
    filepath = './dataset/request_' + serviceName + '.csv'
    f = open(filepath, 'a', newline='')
    with f:
        writer = csv.writer(f)
        response = requests.get('{0}/api/v1/query'.format(configs.PROMETHEUS_URL), params={'query': q})
        if bool(response.json()['data']['result']):
            results = response.json()['data']['result'][0]['value'][1]
            results = float(results)
            results = round(results, 3)
            test.append(results)
        if bool(test):
            writer.writerow(test)

def get_resource_metric(serviceName):
    query1 = 'sum(kube_pod_container_resource_requests{resource="cpu", namespace="default", pod=~"'+ serviceName +'-.*"})'
    response1 = requests.get('{0}/api/v1/query'.format(configs.PROMETHEUS_URL), params={'query': query1})
    if bool(response1.json()['data']['result']):
        results1 = response1.json()['data']['result'][0]['value'][1]
        print(serviceName, results1)
        results1 = float(results1)
        results1 = int(round(results1, 3) / 60 * 100)

    return results1
        

def get_latency_metric(generatorIP, generatorName):
    if generatorName == "generator1":
        slo = 1200
    elif generatorName == "generator2":
        slo = 3000
    elif generatorName == "generator3":
        slo = 900

    query2 = 'locust_requests_current_response_time_percentile_95{instance="'+ generatorIP +':9646", job="'+ generatorName +'"}'
    response2 = requests.get('{0}/api/v1/query'.format(configs.PROMETHEUS_URL), params={'query': query2})
    if bool(response2.json()['data']['result']):
        results2 = response2.json()['data']['result'][0]['value'][1]
        print(results2)
        results2 = float(results2)
        results2 = int(round(results2, 3) / slo *100)

    return results2


def predict(api, model):

    print("------------------------------------------------")
    print("------------------------------------------------")
    print("------------------------------------------------")
    
    service0_action = np.array([[1.5, 10, 1100], [2, 10, 690], [2, 15, 1000], [2.5, 10, 500], [2.5, 15, 730], [2.5, 20, 890], [2.5, 25, 1100], [3, 10, 390], [3, 20, 700], [3, 30, 900], [3, 35, 960], [3.5, 10, 340], [3.5, 20, 530], [3.5, 30, 530], [3.5, 40, 990], [3.5, 45, 1000], [4, 10, 230], [4, 20, 450], [4, 30, 670], [4, 40, 820], [4, 50, 1000], [4, 60, 1100]]) #22 actions
    service1_action = np.array([[3, 10, 2500], [4, 10, 1800], [4, 15, 2600], [5, 10, 1400], [5, 15, 2100], [5, 20, 2600], [6, 10, 1100], [6, 15, 1700], [6, 20, 2300], [6, 25, 2900]]) #10 actions
    service2_action = np.array([[0.5, 10, 900], [1, 10, 420], [1, 15, 630], [1, 20, 800], [2, 10, 370], [2, 15, 560], [2, 20, 700], [2, 25, 860]]) #8 actions

    state[0] = get_resource_metric("deploy-a")
    state[3] = get_resource_metric("sentiment")
    state[6] = get_resource_metric("numberreg")

    state[1] = get_latency_metric("192.168.26.42", "generator1")
    state[4] = get_latency_metric("192.168.26.20", "generator2")
    state[7] = get_latency_metric("192.168.26.41", "generator3")

    get_traffic_metric("192.168.26.42", "generator1", "house")
    get_traffic_metric("192.168.26.20", "generator2", "senti")
    get_traffic_metric("192.168.26.41", "generator3", "numbr")
    predicted_house, predicted_senti, predicted_numbr = rolling_update.predict_traffic()
    print("house: " + str(predicted_house))
    print("senti: " + str(predicted_senti))
    print("numbr: " + str(predicted_numbr))
    
    
    state[2] = int(float(str(predicted_house)))
    state[5] = int(float(str(predicted_senti)))
    state[8] = int(float(str(predicted_numbr)))

    print("Input state: ", state)

    action, _ = model.predict(state)

    print("Action: ", service0_action[action[0]], service1_action[action[1]], service2_action[action[2]])

    servicehouse_resource = int(service0_action[action[0]][0] * 1000)
    servicehouse_concurrency = int(service0_action[action[0]][1])
    servicehouse_podcount = int(math.ceil(state[2] / service0_action[action[0]][1] / 0.7))
    servicesenti_resource = int(service1_action[action[1]][0] * 1000)
    servicesenti_concurrency = int(service1_action[action[1]][1])
    servicesenti_podcount = int(math.ceil(state[5] / service1_action[action[1]][1] / 0.7))
    servicenumbr_resource = int(service2_action[action[2]][0] * 1000)
    servicenumbr_concurrency = int(service2_action[action[2]][1])
    servicenumbr_podcount = int(math.ceil(state[8] / service2_action[action[2]][1] / 0.7))   

    # service0_resource = math.ceil(state[2] / service0_action[action[0]][1] / 0.7) * service0_action[action[0]][0]
    # service1_resource = math.ceil(state[5] / service1_action[action[1]][1] / 0.7) * service1_action[action[1]][0]
    # service2_resource = math.ceil(state[8] / service2_action[action[2]][1] / 0.7) * service2_action[action[2]][0]
    # total_resource = service0_resource + service1_resource + service2_resource

    # service0_sub_reward = 1200 / service0_action[action[0]][2]
    # service1_sub_reward = 3000 / service1_action[action[1]][2]
    # service2_sub_reward = 900 / service2_action[action[2]][2]

    # reward = 100*(service0_sub_reward + service1_sub_reward + service2_sub_reward + 60/total_resource)
    # print("Action: ", action, "Reward: ", str(reward))

    # nextstate_service0_resource = service0_resource / 60 * 100
    # nextstate_service1_resource = service1_resource / 60 * 100
    # nextstate_service2_resource = service2_resource / 60 * 100
    # state[0] = int(nextstate_service0_resource)
    # state[3] = int(nextstate_service1_resource)
    # state[6] = int(nextstate_service2_resource)

    # nextstate_service0_latency = service0_action[action[0]][2] / 1200 * 100
    # nextstate_service1_latency = service1_action[action[1]][2] / 3000 * 100
    # nextstate_service2_latency = service2_action[action[2]][2] / 900 * 100
    # state[1] = int(nextstate_service0_latency)
    # state[4] = int(nextstate_service1_latency)
    # state[7] = int(nextstate_service2_latency)

    # print("Next RS-Lat state: ", state)


    DRL_Action_resource = {
		"apiVersion": "drlscaling.knativescaling.dcn.ssu.ac.kr/v1",
		"kind": "DRLScaleAction",
		"metadata": {"name": "drl-action"},
		"spec": {
			"servicehouse_resource": str(servicehouse_resource)+"m",
			"servicehouse_concurrency": str(servicehouse_concurrency),
            "servicehouse_podcount": str(servicehouse_podcount),
            "servicesenti_resource": str(servicesenti_resource)+"m",
            "servicesenti_concurrency": str(servicesenti_concurrency),
            "servicesenti_podcount": str(servicesenti_podcount),
            "servicenumbr_resource": str(servicenumbr_resource)+"m",
            "servicenumbr_concurrency": str(servicenumbr_concurrency),
            "servicenumbr_podcount": str(servicenumbr_podcount)
		}
	}
    
    list = api.list_namespaced_custom_object(
        group="drlscaling.knativescaling.dcn.ssu.ac.kr",
		version="v1",
		namespace="default",
		plural="drlscaleactions" 
	)

    if len(list['items']) == 0:
        flag = False
    else:
        flag = False
        for item in list['items']:
            if "drl-action" in item['metadata']['name']:
                flag = True

    if flag != True: 
  
        api.create_namespaced_custom_object(
			group="drlscaling.knativescaling.dcn.ssu.ac.kr",
			version="v1",
			namespace="default",
			plural="drlscaleactions",
			body=DRL_Action_resource,
		)
        print("Resource created")
	
    else:

        api.patch_namespaced_custom_object(
        group="drlscaling.knativescaling.dcn.ssu.ac.kr",
        version="v1",
        name="drl-action",
        namespace="default",
        plural="drlscaleactions",
        body=DRL_Action_resource,
    )

if __name__ == '__main__':
    os.system("cp dataset/request_house.bak dataset/request_house.csv")
    os.system("cp dataset/request_senti.bak dataset/request_senti.csv")
    os.system("cp dataset/request_numbr.bak dataset/request_numbr.csv")
    config.load_kube_config()

    api = client.CustomObjectsApi()

    

    env = environment.ParallelServiceSLO({"test": 10})
    finaltrain_model_path = "/root/DRL_limit_resource_knative_scale/TRPOtanh128_Nov29.zip"
    model = TRPO.load(finaltrain_model_path, env=env)

    schedule.every().minute.at(":55").do(lambda: predict(api, model))
    #schedule.every().minute.at(":25").do(lambda: predict(api))
    #schedule.every().minute.at(":30").do(predict)
    while True:
        schedule.run_pending()
        time.sleep(1)

