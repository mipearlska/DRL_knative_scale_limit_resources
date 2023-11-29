import schedule
import time
import os
from configs import configs
import requests
import csv
import rolling_update
from kubernetes import client, config

def get_metric(generatorIP, generatorName, serviceName):
    #q = 'rate(nginx_ingress_nginx_http_requests_total{app="nginx-ingress", class="nginx"}[15s])'
    #q = 'sum(rate(nginx_ingress_nginx_http_requests_total{app="nginx-ingress", class="nginx"}[15s]))'
    q = 'locust_users{instance="' + generatorIP + ':9646", job="' + generatorName + '"}'
    test = []
    filepath = './dataset/request_' + serviceName + '.csv'
    f = open(filepath, 'a', newline='')
    print(q, filepath)
    with f:
        writer = csv.writer(f)
        response = requests.get('{0}/api/v1/query'.format(configs.PROMETHEUS_URL), params={'query': q})
        if bool(response.json()['data']['result']):
            results = response.json()['data']['result'][0]['value'][1]
            results = float(results)
            results = round(results, 3)
            test.append(results)
        if bool(test):
            print(serviceName+" Collected Rps/Users = {}".format(test[0]))
            writer.writerow(test)

def predict(api):
    get_metric("192.168.26.42", "generator1", "house")
    get_metric("192.168.26.20", "generator2", "senti")
    get_metric("192.168.26.41", "generator3", "numbr")
    predicted_house, predicted_senti, predicted_numbr = rolling_update.predict_traffic()
    print("house: " + str(predicted_house))
    print("senti: " + str(predicted_senti))
    print("numbr: " + str(predicted_numbr))

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

    schedule.every().minute.at(":55").do(lambda: predict(api))
    #schedule.every().minute.at(":25").do(lambda: predict(api))
    #schedule.every().minute.at(":30").do(predict)
    while True:
        schedule.run_pending()
        time.sleep(1)

