import json
import pandas as pd
from enum import Enum
from utils.http_utils import request_handler
from app.enums.sheet_names import SheetName

class AmazonScraper:
    header = {}

    def __init__(self, url, auth_token):
        self.url = url
        self.reviews_df = pd.DataFrame()
        self.products_df = pd.DataFrame()
        self.questions_df = pd.DataFrame()
        self.pricing_df = pd.DataFrame()
        self.init_api_auth(auth_token)

    def init_api_auth(self, auth_token):
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {str(auth_token)}",
        }

    def amazon_search(self, query):
        payload = {
            "target": "amazon_search",
            "query": str(query),
            "parse": True,
            "domain": "in",
            "device_type": "desktop",
            "page_from": "1",
        }
        print(query)
        try:
            response_json = request_handler(
                self.url, "POST", data=payload, headers=self.headers
            )
            results = response_json.get("results")[0].get("content").get("results")
            paid_search_df = pd.DataFrame(results.get("paid"))
            organic_search_df = pd.DataFrame(results.get("organic"))
            amazon_choices_search_df = pd.DataFrame(results.get("amazons_choices"))
            return [
                (SheetName.PAID.value, paid_search_df),
                (SheetName.ORGANIC.value, organic_search_df),
                (SheetName.AMAZON_CHOICES.value, amazon_choices_search_df),
            ]
        except Exception as e:
            print(f"failed to scrape amazon search data due to {e}")
            raise ValueError("failed to get the query result") from e



    def amazon_product(self, product_id):
        payload = {
            "target": "amazon_product",
            "query": str(product_id),
            "domain": "in",
            "device_type": "desktop",
            "parse": True,
        }
        print(product_id)
        try:
            response_json = request_handler(self.url, "POST", payload, self.headers)
            result = response_json.get("results")[0].get("content")
        except Exception as e:
            print(f"error occurred while fetching product data of {product_id}:{e}")
        if "ads" in result:
            result = result["ads"]
            try:
                self.products_df = self.products_df.append(pd.DataFrame(result))
            except Exception as e:
                print(f"an error occurred {e}")
                return

    def amazon_pricing(self, product_id):
        payload = {
            "target": "amazon_pricing",
            "query": str(product_id),
            "domain": "in",
            "device_type": "desktop",
            "parse": True,
        }
        response_json = request_handler(self.url, "POST", payload, self.headers)
        if response_json.get("results")[0].get("status_code") == 404:
            print(f'no pricing found for the product {product_id}')
            return
        result = response_json.get("results")[0].get("content")
        try:
            self.pricing_df = self.products_df.append(pd.DataFrame(result))
        except Exception as e:
            print(f"An error occurred while fetching the pricing of product {product_id}: {e}")
            return

    def amazon_questions(self, product_id):
        payload = {
            "target": "amazon_questions",
            "query": str(product_id),
            "domain": "in",
            "device_type": "desktop",
            "parse": True,
        }

        response_json = request_handler(self.url, "POST", payload, self.headers)
        questions = response_json.get("results")[0].get("content").get("questions")
        if questions is None:
            print(f'no questions associated with product {product_id}')
            return
        for question in questions:
            question["asin"] = (
                response_json.get("results")[0].get("content").get("asin")
            )
        try:
            self.questions_df = self.questions_df.append(pd.DataFrame(questions))
        except Exception as e:
            print(f"An error occurred while fetching the questions of product {product_id}: {e}")
            return

    def amazon_reviews(self, product_id):
        payload = {
            "target": "amazon_reviews",
            "query": str(product_id),
            "domain": "in",
            "device_type": "desktop",
            "parse": True,
        }
        response_json = request_handler(self.url, "POST", payload, self.headers)
        reviews = response_json.get("results")[0].get("content").get("reviews")
        if reviews is None:
            print(f'no reviews associated with product {product_id}')
            return
        for review in reviews:
            review["asin"] = response_json.get("results")[0].get("content").get("asin")
        try:
            self.reviews_df = self.reviews_df.append(pd.DataFrame(reviews))
        except Exception as e:
            print(f"An error occurred while fetching the reviews of product {product_id}: {e}")
            return

    def scrape_products_data(self, product_ids_list):
        products_df = pd.DataFrame()
        for product_id in product_ids_list:
            self.amazon_product(product_id)
            self.amazon_pricing(product_id)
            self.amazon_questions(product_id)
            self.amazon_reviews(product_id)

        return [
            (SheetName.PRODUCTS.value, self.products_df),
            (SheetName.PRICING.value, self.pricing_df),
            (SheetName.QUESTIONS.value, self.questions_df),
            (SheetName.REVIEWS.value, self.reviews_df)
        ]