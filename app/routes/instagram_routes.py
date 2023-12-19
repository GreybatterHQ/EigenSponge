from flask import Blueprint, request
import pandas as pd
from app.data_scraper.instagram import InstagramScraper
from app.utils import create_response, generate_combinations, validate_request_data
from app.enums.error_codes import ErrorCodes
from app.enums.export_format import ExportFormat
from app.cloud_storage.s3_manager import S3Manager
from app.config import Config
from datetime import datetime
from app.enums.sheet_names import SheetName
instagram_bp = Blueprint("v1/instagram", __name__)

s3_manager = S3Manager(
    Config.AWS_ACCESS_KEY_ID, Config.AWS_SECRET_ACCESS_KEY, Config.REGION_NAME
)
instagram_scraper = InstagramScraper(
    Config.REDDIT_SCRAPE_BASE_URL, Config.SOCIAL_MEDIA_AUTH_TOKEN
)


@instagram_bp.route("", methods=["POST"])
def scrape_hashtag_data():
    try:
        data = request.get_json()
        validate_request_data(data, ["brandNames", "hashtags", "exportFormat"])
        brand_names = data.get("brandNames")
        hashtags = data.get("hashtags")
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

        brand_names = [brand.replace(' ', '').lower() for brand in brand_names]
        hashtags = [tag.replace(' ', '').lower() for tag in hashtags]

        input_dataFrame, search_queries_list = generate_combinations(brand_names, hashtags, '')
        store_dict = {"input": input_dataFrame}
        result_df = pd.DataFrame()
        try:
            for query in search_queries_list:
                sheet_name, df = instagram_scraper.scrape_hashtag_data(query)
                if df.empty:
                    continue
                df["search_queries"] = query
                result_df = result_df.append(df)
                print(f'successfully scraped data for hashtag {query}')
        except Exception as e:
            raise ValueError(f"failed to scrape data for hashtag for {query}") from e
        store_dict[sheet_name] = result_df

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"instagram_{timestamp}"

        object_url = s3_manager.store_dataFrame_to_sheet(
            Config.INSTAGRAM_BUCKET_NAME, file_name, export_format.value, store_dict
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

@instagram_bp.route("/users", methods=["POST"])
def scrape_user_data():
    try:
        data = request.get_json()
        validate_request_data(data, ["brandNames", "usernames", "exportFormat"])
        brand_names = data.get("brandNames")
        usernames = data.get("usernames")
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

        input_dataFrame, _ = generate_combinations(brand_names, usernames, '', ['brandName', 'username'])
        store_dict = {"input": input_dataFrame}

        for user in usernames:
            try:
                user_details_list = instagram_scraper.scrape_user_data(user)
                for sheet_name, df in user_details_list:
                    df["username"] = user
                    if sheet_name not in store_dict:
                        print(f'sheet {sheet_name} is not present')
                        store_dict[sheet_name] = df
                    else:
                        print(f'appending data to sheet {sheet_name}')
                        store_dict[sheet_name] = (store_dict[sheet_name]).append(df)
            except Exception as e:
                print(f"failed to scrape data for user {user} due to {e}")
                continue

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"instagram_user_{timestamp}"

        object_url = s3_manager.store_dataFrame_to_sheet(
            Config.INSTAGRAM_BUCKET_NAME, file_name, export_format.value, store_dict
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
