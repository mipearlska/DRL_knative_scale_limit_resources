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

def get_metric(generatorIP, generatorName, serviceName):
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

def predict(api, model):

    print(state)

    service0_action = np.array([[1.5, 10, 1100], [2, 10, 690], [2, 15, 1000], [2.5, 10, 500], [2.5, 15, 730], [2.5, 20, 890], [2.5, 25, 1100], [3, 10, 390], [3, 20, 700], [3, 30, 900], [3, 35, 960], [3.5, 10, 340], [3.5, 20, 530], [3.5, 30, 530], [3.5, 40, 990], [3.5, 45, 1000], [4, 10, 230], [4, 20, 450], [4, 30, 670], [4, 40, 820], [4, 50, 1000], [4, 60, 1100]]) #22 actions
    service1_action = np.array([[3, 10, 2500], [4, 10, 1800], [4, 15, 2600], [5, 10, 1400], [5, 15, 2100], [5, 20, 2600], [6, 10, 1100], [6, 15, 1700], [6, 20, 2300], [6, 25, 2900]]) #10 actions
    service2_action = np.array([[0.5, 10, 900], [1, 10, 420], [1, 15, 630], [1, 20, 800], [2, 10, 370], [2, 15, 560], [2, 20, 700], [2, 25, 860]]) #8 actions

    get_metric("192.168.26.42", "generator1", "house")
    get_metric("192.168.26.20", "generator2", "senti")
    get_metric("192.168.26.41", "generator3", "numbr")
    predicted_house, predicted_senti, predicted_numbr = rolling_update.predict_traffic()
    print("house: " + str(predicted_house))
    print("senti: " + str(predicted_senti))
    print("numbr: " + str(predicted_numbr))
    
    
    state[2] = int(float(str(predicted_house)))
    state[5] = int(float(str(predicted_senti)))
    state[8] = int(float(str(predicted_numbr)))

    action, _ = model.predict(state)

    service0_resource = math.ceil(state[2] / service0_action[action[0]][1] / 0.7) * service0_action[action[0]][0]
    service1_resource = math.ceil(state[5] / service1_action[action[1]][1] / 0.7) * service1_action[action[1]][0]
    service2_resource = math.ceil(state[8] / service2_action[action[2]][1] / 0.7) * service2_action[action[2]][0]
    total_resource = service0_resource + service1_resource + service2_resource

    service0_sub_reward = 1200 / service0_action[action[0]][2]
    service1_sub_reward = 3000 / service1_action[action[1]][2]
    service2_sub_reward = 900 / service2_action[action[2]][2]

    reward = 100*(service0_sub_reward + service1_sub_reward + service2_sub_reward + 60/total_resource)
    print("Action: ", action, "Reward: ", str(reward))

    nextstate_service0_resource = service0_resource / 60 * 100
    nextstate_service1_resource = service1_resource / 60 * 100
    nextstate_service2_resource = service2_resource / 60 * 100
    state[0] = int(nextstate_service0_resource)
    state[3] = int(nextstate_service1_resource)
    state[6] = int(nextstate_service2_resource)

    nextstate_service0_latency = service0_action[action[0]][2] / 1200 * 100
    nextstate_service1_latency = service1_action[action[1]][2] / 3000 * 100
    nextstate_service2_latency = service2_action[action[2]][2] / 900 * 100
    state[1] = int(nextstate_service0_latency)
    state[4] = int(nextstate_service1_latency)
    state[7] = int(nextstate_service2_latency)

    print("Next RS-Lat state: ", state)




    # TrafficStat_resource = {
	# 	"apiVersion": "hybridscaling.knativescaling.dcn.ssu.ac.kr/v1",
	# 	"kind": "TrafficStat",
	# 	"metadata": {"name": "deploy-a-trafficstat-test"},
	# 	"spec": {
	# 		"servicename": "deploy-a",
	# 		"scalinginputtraffic": predicted_traffic
	# 	}
	# }
    
    # list = api.list_namespaced_custom_object(
    #     group="hybridscaling.knativescaling.dcn.ssu.ac.kr",
	# 	version="v1",
	# 	namespace="default",
	# 	plural="trafficstats" 
	# )

    # if len(list['items']) == 0:
    #     flag = False
    # else:
    #     flag = False
    #     for item in list['items']:
    #         if "deploy-a" in item['metadata']['name']:
    #             flag = True

    # if flag != True: 
  
    #     api.create_namespaced_custom_object(
	# 		group="hybridscaling.knativescaling.dcn.ssu.ac.kr",
	# 		version="v1",
	# 		namespace="default",
	# 		plural="trafficstats",
	# 		body=TrafficStat_resource,
	# 	)
    #     print("Resource created")
	
    # else:

    #     api.patch_namespaced_custom_object(
    #     group="hybridscaling.knativescaling.dcn.ssu.ac.kr",
    #     version="v1",
    #     name="deploy-a-trafficstat-test",
    #     namespace="default",
    #     plural="trafficstats",
    #     body=TrafficStat_resource,
    # )

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

