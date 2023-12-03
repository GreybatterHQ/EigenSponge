from flask import Blueprint, request
from app.enums.sheet_names import SheetName
from app.utils import create_response, generate_combinations, validate_request_data
from app.enums.error_codes import ErrorCodes
from app.enums.export_format import ExportFormat
import pandas as pd
from app.cloud_storage.s3_manager import S3Manager
from app.data_scraper.amazon import AmazonScraper
from app.config import Config
from datetime import datetime

amazon_bp = Blueprint("v1/amazon", __name__)

s3_manager = S3Manager(
    Config.AWS_ACCESS_KEY_ID, Config.AWS_SECRET_ACCESS_KEY, Config.REGION_NAME
)
amazonScraper = AmazonScraper(Config.AMAZON_SCRAPE_BASE_URL, Config.API_BASIC_AUTH_TOKEN)


@amazon_bp.route("", methods=["POST"])
def scrape_amazon():
    try:
        data = request.get_json()
        validate_request_data(data, ["brandNames", "searchQueries", "exportFormat"])
        brand_names = data.get("brandNames")
        search_queries = data.get("searchQueries")
        export_format_str = ExportFormat(data.get("exportFormat"))

        # Validate exportFormat as Enum
        try:
            export_format = ExportFormat(export_format_str)
        except ValueError as e:
            return create_response(
                status=False,
                error="invalid exportFormat value",
                status_code=400,
                error_code=ErrorCodes.INVALID_REQUEST,
            )

        input_dataFrame, search_queries_list = generate_combinations(brand_names, search_queries, ' ')
        store_dict = {"input": input_dataFrame}

        for query in search_queries_list:
            print(f'scraping search list for query {query}')
            search_dataFrame_list = amazonScraper.amazon_search(query)
            amazon_product_ids = []
            for sheet_name, df in search_dataFrame_list:
                df["search_query"] = query
                store_dict[sheet_name] = df
                if not df.empty:
                    unique_asin_values = df["asin"].dropna().unique()
                    amazon_product_ids.extend(unique_asin_values)
            amazon_product_ids = list(set(amazon_product_ids))

            products_dataFrame_list = amazonScraper.scrape_products_data(
                amazon_product_ids
            )
            for sheet_name, df in products_dataFrame_list:
                df['search_query'] = query
                store_dict[sheet_name] = df

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"amazon_{timestamp}"
        object_url = s3_manager.store_dataFrame_to_sheet(
            Config.AMAZON_BUCKET_NAME, file_name, export_format.value, store_dict
        )
        return create_response(
            status=True, data={"objectURL": object_url}, status_code=201
        )
    except ValueError as e:
        print(f"operation failed due to {e}")
        return create_response(
            status=False,
            error="failed due to generic server error",
            status_code=500,
            error_code=ErrorCodes.GENERIC_SERVER_ERROR,
        )
