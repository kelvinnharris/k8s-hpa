import requests
import time

while True:
  res = requests.get('http://demo.localdev.me:8080/')
  # print(res)
  # time.sleep(0.2)