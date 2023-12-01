from flask import Blueprint, request
from app.utils import create_response, generate_combinations, validate_request_data
from app.enums.error_codes import ErrorCodes
from app.enums.export_format import ExportFormat
import pandas as pd
from app.cloud_storage.s3_manager import S3Manager
from app.data_scraper.reddit import RedditScraper
from app.config import Config
from datetime import datetime

reddit_bp = Blueprint("v1/reddit", __name__)

s3_manager = S3Manager(
    Config.AWS_ACCESS_KEY_ID, Config.AWS_SECRET_ACCESS_KEY, Config.REGION_NAME
)
redditScraper = RedditScraper(Config.REDDIT_SCRAPE_BASE_URL, Config.SOCIAL_MEDIA_AUTH_TOKEN)


@reddit_bp.route("/subreddit", methods=["POST"])
def scrape_reddit():
    try:
        data = request.get_json()
        validate_request_data(data, ["brandNames", "subreddits", "exportFormat"])
        brand_names = data.get("brandNames")
        subreddit_list = data.get("subreddits")
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

        input_dataFrame, _ = generate_combinations(brand_names, subreddit_list, '')
        store_dict = {"input": input_dataFrame}
        for subreddit in subreddit_list:
            search_dataFrame_list = redditScraper.scrape_data(subreddit)

            for sheet_name, df in search_dataFrame_list:
                print(f'{sheet_name}')
                store_dict[sheet_name] = df

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"reddit_{timestamp}"
        object_url = s3_manager.store_dataFrame_to_sheet(
            Config.REDDIT_BUCKET_NAME, file_name, export_format.value, store_dict
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
