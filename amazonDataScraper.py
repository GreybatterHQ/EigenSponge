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
    response_json_paid= response.json().get('results')[0].get('content').get('results').get('paid')
    response_json_organic= response.json().get('results')[0].get('content').get('results').get('organic')
    response_json_amazon_choices= response.json().get('results')[0].get('content').get('results').get('amazons_choices')
    df = pd.DataFrame(response_json_paid)
    df_organic= pd.DataFrame(response_json_organic)
    df_amazon_choices= pd.DataFrame(response_json_amazon_choices)
    df.to_excel('output_excel_amazon_search_paid.xlsx')
    df_organic.to_excel('output_excel_amazon_search_organic.xlsx')
    df_amazon_choices.to_excel('output_excel_amazon_search_amazon_choices.xlsx')
    


def amazon_product(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_product",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    response_json= response.json().get('results')[0].get('content')
    df = pd.DataFrame(response_json)
    df.to_excel('output_excel_amazon_product'+str(query)+'.xlsx', index=False)

def amazon_pricing(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_pricing",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    response_json= response.json().get('results')[0].get('content')
    df = pd.DataFrame(response_json)
    df.to_excel('output_excel_amazon_pricing'+str(query)+'.xlsx')

def amazon_questions(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_questions",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    response_json= response.json().get('results')[0].get('content').get('questions')
    df = pd.DataFrame(response_json)
    df.to_excel('output_excel_amazon_questions'+str(query)+'.xlsx', index=False)

def amazon_reviews(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_reviews",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    response_json= response.json().get('results')[0].get('content').get('reviews')
    df = pd.DataFrame(response_json)
    df.to_excel('output_excel_amazon_reviews'+str(query)+'.xlsx', index=False)




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

excel_amazon_search= pd.read_excel('input_amazon_search.xlsx')
excel_amazon_product= pd.read_excel('input_amazon_product.xlsx')

print(excel_amazon_search)
print(excel_amazon_product)

#for row in excel_amazon_search.itertuples():
#   print("\n\n\n")
#    amazon_search(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
for row in excel_amazon_product.itertuples():    
    print("\n\n\n")
    #amazon_product(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    print("\n\n\n")
    amazon_pricing(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    print("\n\n\n")
    amazon_questions(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    print("\n\n\n")
    amazon_reviews(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    exit();
    
