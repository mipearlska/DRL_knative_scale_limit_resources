from kubernetes import client, config
from pprint import pprint
import requests
from configs import configs

def main():
	config.load_kube_config()
	# query1 = 'sum(kube_pod_container_resource_requests{resource="cpu", namespace="default", pod=~"numberreg-.*"})'
	# response1 = requests.get('{0}/api/v1/query'.format(configs.PROMETHEUS_URL), params={'query': query1})
	# if bool(response1.json()['data']['result']):
	# 	results1 = response1.json()['data']['result'][0]['value'][1]
	# 	results1 = float(results1)
	# 	results1 = int(round(results1, 3) / 60 * 100)
	# 	print(results1)

	# query2 = 'locust_requests_current_response_time_percentile_95{instance="192.168.26.41:9646", job="generator3"}'
	# response2 = requests.get('{0}/api/v1/query'.format(configs.PROMETHEUS_URL), params={'query': query2})
	# if bool(response2.json()['data']['result']):
	# 	results2 = response2.json()['data']['result'][0]['value'][1]
	# 	results2 = float(results2)
	# 	results2 = int(round(results2, 3) / 900 *100)
	# 	print(results2)

	api = client.CustomObjectsApi()

	DRL_Action_resource = {
		"apiVersion": "drlscaling.knativescaling.dcn.ssu.ac.kr/v1",
		"kind": "DRLScaleAction",
		"metadata": {"name": "drl-action"},
		"spec": {
			"servicehouse_resource": str(2000)+"m",
			"servicehouse_concurrency": str(10),
			"servicehouse_podcount": str(1),
			"servicesenti_resource": str(5000)+"m",
			"servicesenti_concurrency": str(26),
			"servicesenti_podcount": str(6),
			"servicenumbr_resource": str(4000)+"m",
			"servicenumbr_concurrency": str(45),
			"servicenumbr_podcount": str(5)
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


	# TrafficStat_resource = {
	# 	"apiVersion": "hybridscaling.knativescaling.dcn.ssu.ac.kr/v1",
	# 	"kind": "TrafficStat",
	# 	"metadata": {"name": "deploy-a-trafficstat-test"},
	# 	"spec": {
	# 		"servicename": "deploy-a",
	# 		"scalinginputtraffic": "100"
	# 	}
	# }

	# list = api.list_namespaced_custom_object(
    #     group="hybridscaling.knativescaling.dcn.ssu.ac.kr",
	# 	version="v1",
	# 	namespace="default",
	# 	plural="trafficstats" 
	# )

	# if len(list['items']) == 0:
	# 	flag = False
	# else:
	# 	flag = False
	# 	for item in list['items']:
	# 		if "deploy-a" in item['metadata']['name']:
	# 			flag = True

	# if flag != True: 
  
	# 	api.create_namespaced_custom_object(
	# 		group="hybridscaling.knativescaling.dcn.ssu.ac.kr",
	# 		version="v1",
	# 		namespace="default",
	# 		plural="trafficstats",
	# 		body=TrafficStat_resource,
	# 	)
	# 	print("Resource created")
	
	# else:

	# 	api.patch_namespaced_custom_object(
    #     group="hybridscaling.knativescaling.dcn.ssu.ac.kr",
    #     version="v1",
    #     name="deploy-a-trafficstat-test",
    #     namespace="default",
    #     plural="trafficstats",
    #     body=TrafficStat_resource,
    # )

if __name__ == "__main__":
    main()
