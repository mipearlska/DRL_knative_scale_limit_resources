# DRL Agent in Concurrent Service Auto-scaling for Knative Resource quota-based Serverless System paper
https://doi.org/10.1016/j.future.2024.06.019

-input: ML Traffic Prediction of all concurrent services

-output: DRLScaleAction CRD (the Quota-based Knative Hybrid autoscaling Operator uses this as input to apply the scaling action)

## Requirements for running
- Install DRLScaleAction CRD from https://github.com/mipearlska/knative_drl_operator
- Install requirements (Python >= 3.6.9)
```
sudo apt install python3-dev python3-venv libffi-dev gcc libssl-dev git
```
```
python3 -m venv $HOME/DRL_knative_scale_limit_resources
```
```
source $HOME/DRL_knative_scale_limit_resources/bin/activate
```
```
pip install -U pip
```
```
pip install setuptools==65.5.0 pip==21
```
```
pip install wheel==0.38.0
```
- Then
```
pip install -r requirements.txt
```
- Then
```
pip install stable-baselines3
```
```
pip install sb3-contrib
```
- Locust Traffic Generator (https://locust.io/). Recommended install version 2.8.6.
```
pip3 install locust==2.8.6
```
- Locust exporter for Prometheus. Locust exporter cannot fetch 95%,50% latency for some recent versions of Locust (> 3). 
```
sudo docker run -d --net=host containersol/locust_exporter
```
- When deploying Prometheus, add Locust config in values.yaml of Prometheus:
job_name = Locust's job parameter in Prometheus query below
target = "Host_URL_that_run_Locust:9646"
```
prometheus:
  prometheusSpec:
    additionalScrapeConfigs:
      - job_name: "generator1"
        scrape_interval: 2s
        static_configs:
        - targets: ["192.168.26.42:9646"]
      - job_name: "generator2"
        scrape_interval: 2s
        static_configs:
        - targets: ["192.168.26.20:9646"]
      - job_name: "generator3"
        scrape_interval: 2s
        static_configs:
        - targets: ["192.168.26.41:9646"]  
```
- Modify a correct Prometheus URL,port in configs/configs.py
```
PROMETHEUS_URL = "http://192.168.26.42:32000"
```
- Provide correct Prometheus IP and job_name in get_traffic_metric() function inside def predict(api, model) of the main.py file:
```
    get_traffic_metric("192.168.26.42", "generator1", "house")
    get_traffic_metric("192.168.26.20", "generator2", "senti")
    get_traffic_metric("192.168.26.41", "generator3", "numbr")
```
- (Optional) Modify when (which second) to make a prediction in __main__ function of main.py file:
```
schedule.every().minute.at(":55").do(lambda: predict(api))
```
## Running
- Generate Traffic to service by running locust traffic profile (Given sample profile change traffic amount every 1 minute)
```
locust -f locustservicetraffic.py
```
- Run Traffic Prediction service
```
python main.py
```
