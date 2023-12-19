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

state = np.array([10, 25, 34, 20, 64, 28, 10, 55, 16], dtype=int)
gprevAction = np.array([21, 6, 7], dtype=int) #[4,60,1100] / [4,20,2000] / [2,25,860]
gprevPod = np.array([1, 2, 1], dtype=int)
gprevRes = np.array([4, 8, 4], dtype=np.float32)
tervice0_action = np.array([[1.5, 10, 1100], [2, 10, 690], [2, 15, 1000], [2.5, 10, 500], [2.5, 15, 730], [2.5, 20, 890], [2.5, 25, 1100], [3, 10, 390], [3, 20, 700], [3, 30, 900], [3, 35, 960], [3.5, 10, 340], [3.5, 20, 530], [3.5, 30, 530], [3.5, 40, 990], [3.5, 45, 1000], [4, 10, 230], [4, 20, 450], [4, 30, 670], [4, 40, 820], [4, 50, 1000], [4, 60, 1100]]) #22 actions
tervice1_action = np.array([[2, 10, 1500], [2, 15, 2200], [3, 10, 1000], [3, 15, 1500], [4, 10, 800], [4, 15, 1300], [4, 20, 2000]]) #7 actions
tervice2_action = np.array([[0.5, 10, 900], [1, 10, 420], [1, 15, 630], [1, 20, 800], [2, 10, 370], [2, 15, 560], [2, 20, 700], [2, 25, 860]]) #8 actions

# Train0 = [34, 50, 66, 66, 69, 94, 53, 56, 86, 100, 56, 50, 69, 33, 25, 28, 55, 25, 17, 13]
# Train1 = [28, 70, 30, 27, 78, 55, 47, 44, 33, 34, 50, 66, 66, 69, 94, 53, 56, 86, 100, 34]
# Train2 = [16, 25, 47, 33, 15, 19, 13, 25, 50, 40, 66, 35, 55, 80, 33, 41, 22, 16, 18, 14]


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

def resource_calculate(traffic0, traffic1, traffic2, index0, index1, index2, prev0, prev1, prev2, prevPod, prevRes):
  update_resource_service0 = 0
  update_resource_service1 = 0
  update_resource_service2 = 0
  new_resource_service0 = 0
  new_resource_service1 = 0
  new_resource_service2 = 0
  tprevPod = np.array([0, 0, 0], dtype=int)
  tempnewRes = np.array([0, 0, 0], dtype=int)
  decreasePodFlag = np.array([0, 0, 0], dtype=int)
  changeConfigFlag = 0

  tempnewRes[0] = math.ceil(traffic0 / tervice0_action[index0][1] / 0.7) * tervice0_action[index0][0]
  tempnewRes[1] = math.ceil(traffic1 / tervice1_action[index1][1] / 0.7) * tervice1_action[index1][0]
  tempnewRes[2] = math.ceil(traffic2 / tervice2_action[index2][1] / 0.7) * tervice2_action[index2][0]
  tempnewTotalRes = tempnewRes[0] + tempnewRes[1] + tempnewRes[2]

  if tervice0_action[prev0][0] == tervice0_action[index0][0] and tervice0_action[prev0][1] == tervice0_action[index0][1]: #same config
      if math.ceil(traffic0 / tervice0_action[index0][1] / 0.7) < prevPod[0]:
          decreasePodFlag[0] = 1

  if tervice1_action[prev1][0] == tervice1_action[index1][0] and tervice1_action[prev1][1] == tervice1_action[index1][1]: #same config
      if math.ceil(traffic1 / tervice1_action[index1][1] / 0.7) < prevPod[1]:
          decreasePodFlag[1] = 1

  if tervice2_action[prev2][0] == tervice2_action[index2][0] and tervice2_action[prev2][1] == tervice2_action[index2][1]: #same config
      if math.ceil(traffic2 / tervice2_action[index2][1] / 0.7) < prevPod[2]:
          decreasePodFlag[2] = 1

  #if there are service that keep old settings and decrease pod, only create new Revision (update min-scale) if newTotalRes <= Limit and prevTotalres > Limit
  #Otherwise, Dont update (min-scale), (Accept Deploying more pod than actually required)
  temptotalRes = 0
  if decreasePodFlag[0] == 1 or decreasePodFlag[1] == 1 or decreasePodFlag[2] == 1:
      for i in range (0,2):
          if decreasePodFlag[i] == 1:
              temptotalRes += prevRes[i]
          else:
              temptotalRes += tempnewRes[i]

      if tempnewTotalRes > 40:
          changeConfigFlag = 0 #keep old Revision
      elif tempnewTotalRes <= 40:
          if temptotalRes > 40:
              changeConfigFlag = 1 #change



  #ServiceHouse NewResource calculation
  if tervice0_action[prev0][0] == tervice0_action[index0][0] and tervice0_action[prev0][1] == tervice0_action[index0][1]: #same config
      if math.ceil(traffic0 / tervice0_action[index0][1] / 0.7) > prevPod[0]: #increasePod
          if tervice0_action[prev0][2] <= 730: #current SV Latency < 730 (low enough), use normal KHPA
              update_resource_service0 = (math.ceil(traffic0 / tervice0_action[index0][1] / 0.7) - prevPod[0]) * tervice0_action[index0][0]
              new_resource_service0 = prevRes[0] + update_resource_service0
              tprevPod[0] = math.ceil(traffic0 / tervice0_action[index0][1] / 0.7)
          else: #current latency too high, cannot tolerate K-HPA
              update_resource_service0 = math.ceil(traffic0 / tervice0_action[index0][1] / 0.7) * tervice0_action[index0][0]
              new_resource_service0 = update_resource_service0
              tprevPod[0] = math.ceil(traffic0 / tervice0_action[index0][1] / 0.7)
      elif math.ceil(traffic0 / tervice0_action[index0][1] / 0.7) == prevPod[0]: #samePod
          update_resource_service0 = 0
          new_resource_service0 = prevRes[0]
          tprevPod[0] = prevPod[0]
      else: #decreasePod
          if changeConfigFlag == 0: #keepOldRevision Flag
              update_resource_service0 = 0
              new_resource_service0 = prevRes[0]
              tprevPod[0] = prevPod[0]
          else: #ChangeRevision Flag
              update_resource_service0 = math.ceil(traffic0 / tervice0_action[index0][1] / 0.7) * tervice0_action[index0][0]
              new_resource_service0 = update_resource_service0
              tprevPod[0] = math.ceil(traffic0 / tervice0_action[index0][1] / 0.7)
  else: #Different Config
      update_resource_service0 = math.ceil(traffic0 / tervice0_action[index0][1] / 0.7) * tervice0_action[index0][0]
      new_resource_service0 = update_resource_service0
      tprevPod[0] = math.ceil(traffic0 / tervice0_action[index0][1] / 0.7)


  #ServiceSenti NewResource calculation
  if tervice1_action[prev1][0] == tervice1_action[index1][0] and tervice1_action[prev1][1] == tervice1_action[index1][1]: #same config
      if math.ceil(traffic1 / tervice1_action[index1][1] / 0.7) < prevPod[1]: #Decrease Pod
          if changeConfigFlag == 0: # Keep Old Revision Flag
              update_resource_service1 = 0
              new_resource_service1 = prevRes[1]
              tprevPod[1] = prevPod[1]
          else: # Change Revision Flag
              update_resource_service1 = math.ceil(traffic1 / tervice1_action[index1][1] / 0.7) * tervice1_action[index1][0]
              new_resource_service1 = update_resource_service1
              tprevPod[1] = math.ceil(traffic1 / tervice1_action[index1][1] / 0.7)
      else: #Increase Pod
          if tervice1_action[prev1][2] <= 1500 and math.ceil(traffic1/ tervice1_action[index1][1] / 0.7) - prevPod[1] <= 2: #low latency enough and only increase <= 2 pods
              update_resource_service1 = (math.ceil(traffic1 / tervice1_action[index1][1] / 0.7) - prevPod[1]) * tervice1_action[index1][0]
              new_resource_service1 = prevRes[1] + update_resource_service1
              tprevPod[1] = math.ceil(traffic1 / tervice1_action[index1][1] / 0.7)
          else: #high latency
              if math.ceil(traffic1 / tervice1_action[index1][1] / 0.7) == prevPod[1]: #no change in number of pods
                  update_resource_service1 = 0
                  new_resource_service1 = prevRes[1]
                  tprevPod[1] = prevPod[1]
              else: #change in number of pods
                  update_resource_service1 = math.ceil(traffic1 / tervice1_action[index1][1] / 0.7) * tervice1_action[index1][0]
                  new_resource_service1 = update_resource_service1
                  tprevPod[1] = math.ceil(traffic1 / tervice1_action[index1][1] / 0.7)
  else: # Different Config
      update_resource_service1 = math.ceil(traffic1 / tervice1_action[index1][1] / 0.7) * tervice1_action[index1][0]
      new_resource_service1 = update_resource_service1
      tprevPod[1] = math.ceil(traffic1 / tervice1_action[index1][1] / 0.7)

  #ServiceNumber NewResource calculation
  if tervice2_action[prev2][0] == tervice2_action[index2][0] and tervice2_action[prev2][1] == tervice2_action[index2][1]: #same config
      if math.ceil(traffic2 / tervice2_action[index2][1] / 0.7) > prevPod[2]: #increasePod
          if tervice2_action[prev2][2] <= 630: #current SV Latency < 630 (low enough)
              update_resource_service2 = (math.ceil(traffic2/ tervice2_action[index2][1] / 0.7) - prevPod[2]) * tervice2_action[index2][0]
              new_resource_service2 = prevRes[2] + update_resource_service2
              tprevPod[2] = math.ceil(traffic2 / tervice2_action[index2][1] / 0.7)
          else:
              update_resource_service2 = math.ceil(traffic2 / tervice2_action[index2][1] / 0.7) * tervice2_action[index2][0]
              new_resource_service2 = update_resource_service2
              tprevPod[2] = math.ceil(traffic2 / tervice2_action[index2][1] / 0.7)
      elif math.ceil(traffic2 / tervice2_action[index2][1] / 0.7) == prevPod[2]:#SamePod
          update_resource_service2 = 0
          new_resource_service2= prevRes[2]
          tprevPod[2] = prevPod[2]
      else:
          if changeConfigFlag == 0:
              update_resource_service2 = 0
              new_resource_service2= prevRes[2]
              tprevPod[2] = prevPod[2]
          else:
              update_resource_service2 = math.ceil(traffic2 / tervice2_action[index2][1] / 0.7) * tervice2_action[index2][0]
              new_resource_service2 = update_resource_service2
              tprevPod[2] = math.ceil(traffic2 / tervice2_action[index2][1] / 0.7)
  else:
      update_resource_service2 = math.ceil(traffic2 / tervice2_action[index2][1] / 0.7) * tervice2_action[index2][0]
      new_resource_service2 = update_resource_service2
      tprevPod[2] = math.ceil(traffic2 / tervice2_action[index2][1] / 0.7)

  total_update_resource = prevRes[0] + prevRes[1] + prevRes[2] + update_resource_service0 + update_resource_service1 + update_resource_service2

  return new_resource_service0, new_resource_service1, new_resource_service2, total_update_resource, tprevPod


def predict(api, model):

    print("------------------------------------------------")
    print("------------------------------------------------")
    print("------------------------------------------------")
    #print(gprevAction, gprevPod, gprevRes)

    service0_action = np.array([[1.5, 10, 1100], [2, 10, 690], [2, 15, 1000], [2.5, 10, 500], [2.5, 15, 730], [2.5, 20, 890], [2.5, 25, 1100], [3, 10, 390], [3, 20, 700], [3, 30, 900], [3, 35, 960], [3.5, 10, 340], [3.5, 20, 530], [3.5, 30, 530], [3.5, 40, 990], [3.5, 45, 1000], [4, 10, 230], [4, 20, 450], [4, 30, 670], [4, 40, 820], [4, 50, 1000], [4, 60, 1100]]) #22 actions
    service1_action = np.array([[2, 10, 1500], [2, 15, 2200], [3, 10, 1000], [3, 15, 1500], [4, 10, 800], [4, 15, 1300], [4, 20, 2000]]) #7 actions
    service2_action = np.array([[0.5, 10, 900], [1, 10, 420], [1, 15, 630], [1, 20, 800], [2, 10, 370], [2, 15, 560], [2, 20, 700], [2, 25, 860]]) #8 actions

    #state[0] = get_resource_metric("deploy-a")
    #state[3] = get_resource_metric("sentiment")
    #state[6] = get_resource_metric("numberreg")

    # state[1] = get_latency_metric("192.168.26.42", "generator1")
    # state[4] = get_latency_metric("192.168.26.20", "generator2")
    # state[7] = get_latency_metric("192.168.26.41", "generator3")

    get_traffic_metric("192.168.26.42", "generator1", "house")
    get_traffic_metric("192.168.26.20", "generator2", "senti")
    get_traffic_metric("192.168.26.41", "generator3", "numbr")
    predicted_house, predicted_senti, predicted_numbr = rolling_update.predict_traffic()
    
    state[2] = int(float(str(predicted_house)))
    state[5] = int(float(str(predicted_senti)))
    state[8] = int(float(str(predicted_numbr)))

    # state[2] = Train0[index]
    # state[5] = Train1[index]
    # state[8] = Train2[index]
    # predicted_house = Train0[index]
    # predicted_senti = Train1[index]
    # predicted_numbr = Train2[index]

    #print("Input state: ", state)
    # service0_sub_reward = 100 / state[1]
    # service1_sub_reward = 100 / state[4]
    # service2_sub_reward = 100 / state[7]
    # total_resource = state[0] + state[3] + state[6]
    # total_reward = 100*(service0_sub_reward + service1_sub_reward + service2_sub_reward + 100/total_resource)
    # print("Input state REWARD: ", total_reward)

    action, _ = model.predict(state)

    res1, res2, res3, upRestotal, tprevPod = resource_calculate(predicted_house, predicted_senti, predicted_numbr, action[0], action[1], action[2], gprevAction[0], gprevAction[1], gprevAction[2], gprevPod, gprevRes)
    gprevAction[0] = action[0]
    gprevAction[1] = action[1]
    gprevAction[2] = action[2]
    gprevPod[0] = tprevPod[0]
    gprevPod[1] = tprevPod[1]
    gprevPod[2] = tprevPod[2]
    gprevRes[0] = res1
    gprevRes[1] = res2
    gprevRes[2] = res3
    #print(gprevAction, gprevPod, gprevRes)

    print("Updating resource usage - After update", upRestotal, res1+res2+res3)
    if upRestotal <= 40:
        print("Below Limit")
    
    print("ActionHouse: ", service0_action[action[0]][0], service0_action[action[0]][1])
    print("ActionSenti: ", service0_action[action[1]][0], service0_action[action[1]][1])
    print("ActionNumbr: ", service0_action[action[2]][0], service0_action[action[2]][1])
    print("housepod", gprevPod[0])
    print("sentipod", gprevPod[1])
    print("numbrpod", gprevPod[2])

    servicehouse_resource = int(service0_action[action[0]][0] * 1000)
    servicehouse_concurrency = int(service0_action[action[0]][1])
    servicehouse_podcount = int(gprevPod[0])
    servicesenti_resource = int(service1_action[action[1]][0] * 1000)
    servicesenti_concurrency = int(service1_action[action[1]][1])
    servicesenti_podcount = int(gprevPod[1])
    servicenumbr_resource = int(service2_action[action[2]][0] * 1000)
    servicenumbr_concurrency = int(service2_action[action[2]][1])
    servicenumbr_podcount = int(gprevPod[2])   

    # service0_resource = math.ceil(state[2] / service0_action[action[0]][1] / 0.7) * service0_action[action[0]][0]
    # service1_resource = math.ceil(state[5] / service1_action[action[1]][1] / 0.7) * service1_action[action[1]][0]
    # service2_resource = math.ceil(state[8] / service2_action[action[2]][1] / 0.7) * service2_action[action[2]][0]
    # total_resource = service0_resource + service1_resource + service2_resource

    # service0_sub_reward = 1200 / service0_action[action[0]][2]
    # service1_sub_reward = 3000 / service1_action[action[1]][2]
    # service2_sub_reward = 900 / service2_action[action[2]][2]

    # reward = 100*(service0_sub_reward + service1_sub_reward + service2_sub_reward + 60/total_resource)
    # print("Action: ", action, "Reward: ", str(reward))

    nextstate_service0_resource = res1 / 40 * 100
    nextstate_service1_resource = res2 / 40 * 100
    nextstate_service2_resource = res3 / 40 * 100
    state[0] = int(nextstate_service0_resource)
    state[3] = int(nextstate_service1_resource)
    state[6] = int(nextstate_service2_resource)

    nextstate_service0_latency = service0_action[action[0]][2] / 1200 * 100
    nextstate_service1_latency = service1_action[action[1]][2] / 2200 * 100
    nextstate_service2_latency = service2_action[action[2]][2] / 900 * 100
    state[1] = int(nextstate_service0_latency)
    state[4] = int(nextstate_service1_latency)
    state[7] = int(nextstate_service2_latency)

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


    

    env = environment.Parallel2({"test": 10})
    finaltrain_model_path = "/root/DRL_limit_resource_knative_scale/B_tt_TRPOtanh128.zip"
    model = TRPO.load(finaltrain_model_path, env=env)

    # for i in range (19):
    #     predict(api, model, i)
    schedule.every(2).minutes.at(":55").do(lambda: predict(api, model))
    #schedule.every().minute.at(":25").do(lambda: predict(api))
    #schedule.every().minute.at(":30").do(predict)
    while True:
        schedule.run_pending()
        time.sleep(1)


