from flask import Blueprint, request
from app.data_scraper.instagram import InstagramScraper
from app.utils import create_response, generate_combinations, validate_request_data
from app.enums.error_codes import ErrorCodes
from app.enums.export_format import ExportFormat
from app.cloud_storage.s3_manager import S3Manager
from app.config import Config
from datetime import datetime

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

        input_dataFrame, search_queries_list = generate_combinations(brand_names, hashtags, '')
        store_dict = {"input": input_dataFrame}
        try:
            for query in search_queries_list:
                sheet_name, df = instagram_scraper.scrape_hashtag_data(query)
                df["search_query"] = query
                print(f'successfully scraped data for hashtag {query}')
        except Exception as e:
            raise ValueError("failed to scrape data for hashtag") from e
        store_dict[sheet_name] = df

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
        username = request.args.get('username')
        data = request.get_json()
        validate_request_data(data, ["brandNames", "exportFormat"])
        brand_names = data.get("brandNames")
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

        input_dataFrame, _ = generate_combinations(brand_names, '')
        store_dict = {"input": input_dataFrame}
        try:
            user_details_list = instagram_scraper.scrape_user_data(username)
            for sheet_name, df in user_details_list:
                df["search_query"] = brand_names
                store_dict[sheet_name] = df
        except Exception as e:
            print(f"failed to scrape data for user {username} due to {e}")
            raise ValueError(f"failed to scrape data for user {username}") from e

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"instagram_user_{username}_{timestamp}"

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
