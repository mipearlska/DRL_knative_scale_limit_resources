from datetime import datetime

import pytz
import random
import requests
import os
import json
import yaml
from yaml.loader import SafeLoader
from configs import configs
#from kubernetes import client, config
import joblib
import predict
import time

def get_template_deployment(deployment_name):
    cmd = "kubectl get deploy {} -n default -o yaml > ./template/info.yaml".format(deployment_name)
    os.system(cmd)
    with open("./template/info.yaml", "r") as file:
        data = yaml.load(file, Loader=SafeLoader)
    temp = data["metadata"]["annotations"]["kubectl.kubernetes.io/last-applied-configuration"]
    temp = json.loads(temp)   #convert class str to dict before dump yaml
    with open("./template/template.yaml", "w") as file:
        yaml.dump(temp, file)

def get_deployment_name():
    with open("./template/template.yaml", "r") as file:
        data = yaml.load(file, Loader=SafeLoader)
    cur_name = data["metadata"]["name"]
    return cur_name

def get_running_deployment(app_label):
    q1 = 'count(kube_pod_container_status_running{' + 'container="{}"'.format(app_label) + '}) by (container)'
    q2 = 'kube_pod_container_resource_limits{' + 'container="{}"'.format(app_label) + '} * 1000'
    response = requests.get('{0}/api/v1/query'.format(configs.PROMETHEUS_URL), params={'query': q1})
    if bool(response.json()['data']['result']):
        results = response.json()['data']['result'][0]['value'][1]
        cur_pod = int(results)
    response = requests.get('{0}/api/v1/query'.format(configs.PROMETHEUS_URL), params={'query': q2})
    if bool(response.json()['data']['result']):
        results = response.json()['data']['result'][0]['value'][1]
        cur_res = int(results)
    return cur_pod, cur_res

def horizontal_scale(cur_name, replicas):
    cmd = 'kubectl scale deployment/{} --replicas={}'.format(cur_name, replicas)
    os.system(cmd)

def update_template(update_name, pred_pod, pred_res):
    file_name = "./template/template.yaml"
    with open(file_name) as f:
        doc = yaml.safe_load(f)
    doc['metadata']['name'] = update_name
    doc['spec']['replicas'] = pred_pod
    pred_res = "{}m".format(pred_res)
    doc['spec']['template']['spec']['containers'][0]["resources"]['limits']['cpu'] = pred_res
    with open(file_name, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def create_new_deployment():
    path = "./template/template.yaml"
    cmd = "kubectl apply -f {}".format(path)
    os.system(cmd)

def delete_deployment(cur_name):
    cmd = "kubectl delete deployment {}".format(cur_name)
    os.system(cmd)

def rolling_update_deployment():

    model_path = configs.MODEL_PATH
    scaler_path = configs.SCALER_PATH
    data_path = configs.COLLECTED_DATA_PATH
    burst = configs.BURST
    app_label = os.getenv('APP_LABEL', configs.APP_LABEL)
    deployment_name = os.getenv('DEPLOYMENT_NAME', configs.DEPLOYMENT_NAME)

    temp_path = "./template/template.yaml"
    if os.path.exists(temp_path):
        print("Template existed!")
    else:
        get_template_deployment(deployment_name)
        print("Get template successfully!")

    workload = predict.predict_workload(model_path, scaler_path, data_path)

    print("pred_workload = {}".format(workload))
    performance_model = joblib.load(configs.PERFORMANCE_MODEL_PATH)
    Resource = [600.0, 700.0, 800.0, 850.0, 900.0, 950.0]

    cur_name = get_deployment_name()
    print("Cur_name = {}".format(cur_name))

    cur_pod, cur_res = get_running_deployment(app_label)
    print("Cur_pod = {}, Cur_res = {}".format(cur_pod, cur_res))

    if workload > burst:
        row = [workload, 950.0]
        yhat = performance_model.predict([row])
        pred_pod = round(yhat[0][0])
        pred_res = 950.0
        print("pred_pod = {}, pred_res = {}".format(pred_pod, pred_res))
        if cur_res == pred_res:
            if pred_pod == cur_pod:
                print("Do nothing")
            elif pred_pod > cur_pod:
                horizontal_scale(cur_name, pred_pod)
                print("Horizontal scale up from {} to {} pods".format(cur_pod, pred_pod))
            else:
                time.sleep(12)
                horizontal_scale(cur_name, pred_pod)
                print("Horizontal scale down from {} to {} pods".format(cur_pod, pred_pod))
        else:
            count = int(configs.COUNT) + random.randint(0, 1000)
            update_name = "{}{}".format(deployment_name, count)
            print("updated_name = {}".format(update_name))

            # create new yaml file and deploy new deployment
            update_template(update_name, pred_pod, pred_res)
            print("Updated new deployment yaml")
            create_new_deployment()
            print("creating new deployment")

            # once new deployment runs, terminate old deployment
            time.sleep(10)
            print("created new deployment")
            delete_deployment(cur_name)
            print("deleted old deployment")
            print("finish hybrid scaling")
    else:
        values = [0, 0]
        max = 0
        for R in Resource:
            row = [workload, R]
            yhat = performance_model.predict([row])  # [[N_pods , Pod_utilization]]
            N_pods = round(yhat[0][0])
            Pod_util = yhat[0][1]
            if Pod_util > max:
                values = [N_pods, R]
                max = Pod_util
        pred_pod = values[0]
        pred_res = values[1]
        print("pred_pod = {}, pred_res = {}".format(pred_pod, pred_res))
        if cur_res == pred_res:
            if pred_pod == cur_pod:
                print("Do nothing")
            elif pred_pod > cur_pod:

                horizontal_scale(cur_name, pred_pod)
                print("Horizontal scale up from {} to {} pods".format(cur_pod, pred_pod))
            else:
                time.sleep(12)
                horizontal_scale(cur_name, pred_pod)
                print("Horizontal scale down from {} to {} pods".format(cur_pod, pred_pod))
        else:
            count = int(configs.COUNT) + random.randint(0, 1000)
            update_name = "{}{}".format(deployment_name, count)
            print("updated_name = {}".format(update_name))
            # create new yaml file and deploy new deployment
            update_template(update_name, pred_pod, pred_res)
            print("Updated new deployment yaml")
            create_new_deployment()
            print("creating new deployment")

            # once new deployment runs, terminate old deployment
            time.sleep(10)
            print("created new deployment")
            delete_deployment(cur_name)
            print("deleted old deployment")
            print("finish hybrid scaling")

def predict_traffic():
    model_path = configs.MODEL_PATH
    scaler_path = configs.SCALER_PATH
    data_path_house = configs.COLLECTED_DATA_PATH_APP_HOUSE
    data_path_senti = configs.COLLECTED_DATA_PATH_APP_SENTI
    data_path_numbr = configs.COLLECTED_DATA_PATH_APP_NUMBR
    burst = configs.BURST
    app_label = os.getenv('APP_LABEL', configs.APP_LABEL)
    deployment_name = os.getenv('DEPLOYMENT_NAME', configs.DEPLOYMENT_NAME)

    temp_path = "./template/template.yaml"
    if os.path.exists(temp_path):
        print("Template existed!")
    else:
        get_template_deployment(deployment_name)
        print("Get template successfully!")

    workload_house = predict.predict_workload(model_path, scaler_path, data_path_house)
    workload_senti = predict.predict_workload(model_path, scaler_path, data_path_senti)
    workload_numbr = predict.predict_workload(model_path, scaler_path, data_path_numbr)

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current time = {}".format(current_time))
    return workload_house, workload_senti, workload_numbr
