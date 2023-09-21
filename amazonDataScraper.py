import json
import requests
import pandas as pd

def amazon_search():
    return null
def amazon_product():
    return null

with open("config.json","r") as config_file:
    config = json.load(config_file)

api_key = config['api_key']
api_password = config['api_password']
api_basic_auth = config['api_basic_auth_token']

excel= pd.read_excel('input.xlsx')

print(excel[0])

products=amazon_search()
amazon_product(products)