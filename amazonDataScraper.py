import json
import requests
import pandas as pd

def amazon_search( api_basic_auth_token, query):
    url = "https://scrape.smartproxy.com/v1/tasks"

    payload = {
      "target": "amazon_search",
      "query": str(query),
      "parse": True,
      "domain": "in",
      "device_type": "desktop",
      "page_from": "1"
      }

    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic "+ str(api_basic_auth_token)
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)

with open("config.json","r") as config_file:
    config = json.load(config_file)

api_key = config['api_key']
api_password = config['api_password']
api_basic_auth = config['api_basic_auth_token']

excel= pd.read_excel('input.xlsx')

print(excel)

for row in excel.itertuples():
    print(row[1])
    amazon_search(api_basic_auth_token=api_basic_auth,query=row[1])
