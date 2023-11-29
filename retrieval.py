import csv
import requests
import sys
import schedule
import time
from itertools import zip_longest
from configs import configs
def get_metric():
    q = 'rate(nginx_ingress_nginx_http_requests_total{app="nginx-ingress", class="nginx"}[15s])'
    test = []
    f = open('./dataset/request.csv', 'a', newline='')
    with f:
        writer = csv.writer(f)
        response = requests.get('{0}/api/v1/query'.format(configs.PROMETHEUS_URL), params={'query': q})
        if bool(response.json()['data']['result']):
            results = response.json()['data']['result'][0]['value'][1]
            results = float(results)
            results = round(results, 3)
            test.append(results + 2)
        if bool(test):
            writer.writerow(test)

schedule.every(20).seconds.do(get_metric)
while True:
    schedule.run_pending()
    time.sleep(1)
