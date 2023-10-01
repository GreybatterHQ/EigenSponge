import json
import requests
import pandas as pd

def amazon_search( api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_search",
      "query": str(query),
      "parse": True,
      "domain": "in",
      "device_type": "desktop",
      "page_from": "1"
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

def amazon_bestsellers(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_bestsellers",
      "query": str(query),
      "parse": True,
      "domain": "in",
       "device_type": "desktop",
      "geo": "10001"
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

def amazon_product(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_product",
      "query": "B09H74FXNW",
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

def amazon_pricing(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_pricing",
      "query": "B09H74FXNW",
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

def amazon_questions(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_questions",
      "query": "B09H74FXNW",
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

def amazon_reviews(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_reviews",
      "query": "B09H74FXNW",
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)




with open("config.json","r") as config_file:
    config = json.load(config_file)

api_key = config['api_key']
api_password = config['api_password']
api_basic_auth = config['api_basic_auth_token']

url = "https://scrape.smartproxy.com/v1/tasks"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic "+ str(api_basic_auth)
   }

excel= pd.read_excel('input.xlsx')

print(excel)

for row in excel.itertuples():
    print("\n\n\n")
    print(row[1])
    print("\n\n\n")
    amazon_search(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    print("\n\n\n")
    amazon_bestsellers(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    print("\n\n\n")
    amazon_product(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    print("\n\n\n")
    amazon_pricing(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    print("\n\n\n")
    amazon_questions(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    print("\n\n\n")
    amazon_reviews(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
