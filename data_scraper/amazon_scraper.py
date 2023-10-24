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
from utils.http_utils import request_handler
from utils.excel_utils import save_dataFrame_to_excel

result_directory = 'output'
file_name = 'output_excel_amazon.xlsx'

class SheetName(Enum):
    PAID = "paid"
    ORGANIC = "organic"
    AMAZON_CHOICES = "amazon_choices"
    REVIEWS = "reviews"
    PRICING = "pricing"
    PRODUCTS = "products"
    QUESTIONS = "questions"

class AmazonScraper:
  header = {}
  def __init__(self, url, config_path):
    self.url = url
    self.config_path = config_path
    self.reviews_df = pd.DataFrame()
    self.products_df = pd.DataFrame()
    self.questions_df = pd.DataFrame()
    self.pricing_df = pd.DataFrame()
    self.paid_search_df = pd.DataFrame()
    self.amazon_choices_search_df = pd.DataFrame()
    self.organic_search_df = pd.DataFrame()

  def init_api_auth(self):
    with open(self.config_path,"r") as config_file:
      config = json.load(config_file)
    self.headers = {
          "accept": "application/json",
          "content-type": "application/json",
          "authorization": "Basic "+ config['api_basic_auth_token']
    }

  def amazon_search(self, query):
    payload = {
      "target": "amazon_search",
      "query": str(query),
      "parse": True,
      "domain": "in",
      "device_type": "desktop",
      "page_from": "1"
      }

    response_json = request_handler(self.url, 'POST', data=payload, headers=self.headers)
    results = response_json.get('results')[0].get('content').get('results')

    self.paid_search_df = self.paid_search_df.append(results.get('paid'))
    self.organic_search_df = self.organic_search_df.append(results.get('organic'))
    self.amazon_choices_search_df = self.amazon_choices_search_df.append(results.get('amazons_choices'))


  def amazon_product(self, query):
    payload = {
      "target": "amazon_product",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    print(query)
    try:
      response_json = request_handler(self.url, 'POST', payload, self.headers)
      result = response_json.get('results')[0].get('content')
    except Exception as e:
      print(f'error occurred while fetching data {e}')
      return
    if 'ads' in result:
        result = result['ads']
        try:
          self.products_df = self.products_df.append(pd.DataFrame(result))
        except Exception as e:
          print(f"an error occurred {e}")
          return


  def amazon_pricing(self, query):
    payload = {
      "target": "amazon_pricing",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response_json = request_handler(self.url, 'POST', payload, self.headers)
    result = response_json.get('results')[0].get('content')    
    try:
      self.pricing_df = self.products_df.append(pd.DataFrame(result))
    except Exception as e:
      print(f"An error occurred: {e}")
      return


  def amazon_questions(self, query):
    payload = {
      "target": "amazon_questions",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }

    response_json = request_handler(self.url, 'POST', payload, self.headers)
    questions = response_json.get('results')[0].get('content').get('questions')
    try:
      self.questions_df = self.questions_df.append(pd.DataFrame(questions))
    except Exception as e:
      print(f"An error occurred: {e}")
      return

  def amazon_reviews(self, query):
    payload = {
      "target": "amazon_reviews",
      "query": str(query),
      "domain": "in",
      "device_type": "desktop",
      "parse": True
      }
    response_json = request_handler(self.url, 'POST', payload, self.headers)
    reviews = response_json.get('results')[0].get('content').get('reviews')
    try:
      self.reviews_df = self.reviews_df.append(pd.DataFrame(reviews))
    except Exception as e:
      print(f"An error occurred: {e}")
      return

  def scrape_amazon_data(self):
    self.init_api_auth()

    try:
      excel_amazon_search= pd.read_excel('input_amazon_search.xlsx')
      excel_amazon_product= pd.read_excel('input_amazon_product.xlsx')
    except FileNotFoundError:
      print('input file not found')
      exit()

    # print('printing the search input:', excel_amazon_search)
    # print('amazon product:',excel_amazon_product)

    for row in excel_amazon_search.itertuples():
      self.amazon_search(query=row[1])
    
    save_dataFrame_to_excel(file_name, SheetName.PAID.value, self.paid_search_df, result_directory)
    save_dataFrame_to_excel(file_name, SheetName.ORGANIC.value, self.organic_search_df, result_directory)
    save_dataFrame_to_excel(file_name, SheetName.AMAZON_CHOICES.value, self.amazon_choices_search_df, result_directory)
    for row in excel_amazon_product.itertuples():
      # print("\n\n\n")
      self.amazon_product(query=row[1])
      # print("\n\n\n")
      self.amazon_pricing(query=row[1])
      # print("\n\n\n")
      self.amazon_questions(query=row[1])
      # print("\n\n\n")
      self.amazon_reviews(query=row[1])
    save_dataFrame_to_excel(file_name, SheetName.PRODUCTS.value, self.products_df, result_directory)
    save_dataFrame_to_excel(file_name, SheetName.PRICING.value, self.pricing_df, result_directory)
    save_dataFrame_to_excel(file_name, SheetName.QUESTIONS.value, self.questions_df, result_directory)
    save_dataFrame_to_excel(file_name, SheetName.REVIEWS.value, self.reviews_df, result_directory)