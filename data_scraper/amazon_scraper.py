import sys
import os
# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory path
parent_dir = os.path.dirname(current_dir)

# Append the parent directory to the system path
sys.path.append(parent_dir)
import json
import requests
import pandas as pd
from openpyxl import load_workbook, Workbook
from enum import Enum
import numpy as np
from utils.http_utils import request_handler
from utils.excel_utils import save_dataFrame_to_excel

result_directory = 'output'
file_name = 'amazon_search.xlsx'

class SheetName(Enum):
    PAID = "paid"
    ORGANIC = "organic"
    AMAZON_CHOICES = "amazon_choices"
    REVIEWS = "reviews"
    PRICING = "pricing"
    PRODUCTS = "products"
    QUESTIONS = "questions"

def amazon_search(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_search",
      "query": str(query),
      "parse": True,
      "domain": "in",
      "device_type": "desktop",
      "page_from": "1"
      }

    response_json = request_handler(url, 'POST', data=payload, headers=headers)
    results = response_json.get('results')[0].get('content').get('results')


    df_paid = pd.DataFrame(results.get('paid'))
    df_organic= pd.DataFrame(results.get('organic'))
    df_amazon_choices= pd.DataFrame(results.get('amazons_choices'))
    save_dataFrame_to_excel(file_name, SheetName.PAID.value, df_paid, result_directory)
    save_dataFrame_to_excel(file_name, SheetName.ORGANIC.value, df_organic, result_directory)
    save_dataFrame_to_excel(file_name, SheetName.AMAZON_CHOICES.value, df_amazon_choices, result_directory)


def amazon_product(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_product",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }

    response_json = request_handler(url, 'POST', payload, headers)
    print(response_json)
    result = response_json.get('results')[0].get('content')
    print('result:', pd.DataFrame(result))
    save_dataFrame_to_excel('output_excel_amazon.xlsx', SheetName.PRODUCTS.value, pd.DataFrame(result), result_directory)

def amazon_pricing(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_pricing",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response_json = request_handler(url, 'POST', payload, headers)
    result = response_json.get('results')[0].get('content')
    save_dataFrame_to_excel('output_excel_amazon.xlsx', SheetName.PRICING.value, pd.DataFrame(result), result_directory)

def amazon_questions(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_questions",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }

    response_json = request_handler(url, 'POST', payload, headers)
    questions = response_json.get('results')[0].get('content').get('questions')
    save_dataFrame_to_excel('output_excel_amazon.xlsx', SheetName.QUESTIONS.value, pd.DataFrame(questions), result_directory)

def amazon_reviews(api_basic_auth_token, query, url, headers):
    payload = {
      "target": "amazon_reviews",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response_json = request_handler(url, 'POST', payload, headers)
    reviews = response_json.get('results')[0].get('content').get('reviews')
    save_dataFrame_to_excel('output_excel_amazon.xlsx', SheetName.REVIEWS.value, pd.DataFrame(reviews), result_directory)

def init_api_auth(config_path):
  with open(config_path,"r") as config_file:
    config = json.load(config_file)
  return config['api_basic_auth_token']


def scrape_amazon_data():
  api_basic_auth = init_api_auth("config_2.json")
  url = "https://scrape.smartproxy.com/v1/tasks"
  headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic "+ api_basic_auth
    }

  try:
    excel_amazon_search= pd.read_excel('input_amazon_search.xlsx')
    excel_amazon_product= pd.read_excel('input_amazon_product.xlsx')
  except FileNotFoundError:
    print('input file not found')
    exit()

  # print('printing the search input:', excel_amazon_search)
  # print('amazon product:',excel_amazon_product)

  # for row in excel_amazon_search.itertuples():
    # print("\n\n\n")
    # amazon_search(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
  for row in excel_amazon_product.itertuples():    
  #   print("\n\n\n")
    # amazon_product(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
  #   print("\n\n\n")
    # amazon_pricing(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
  #   print("\n\n\n")
    # amazon_questions(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
  #   print("\n\n\n")
    amazon_reviews(api_basic_auth_token=api_basic_auth,query=row[1], url=url, headers=headers)
    
