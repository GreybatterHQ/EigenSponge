from datetime import datetime
import os
from urllib.parse import urlparse
from flask import Blueprint, request
from app.utils import create_response, validate_request_data
from app.enums.error_codes import ErrorCodes
from app.enums.export_format import ExportFormat
import pandas as pd
from app.cloud_storage.s3_manager import S3Manager
from app.config import Config

appends_bp = Blueprint("v1/appends", __name__)

s3_manager = S3Manager(
    Config.AWS_ACCESS_KEY_ID, Config.AWS_SECRET_ACCESS_KEY, Config.REGION_NAME
)

bucket_name_prefixes = {
    Config.AMAZON_BUCKET_NAME: 'amazon',
    Config.INSTAGRAM_BUCKET_NAME: 'instagram',
    Config.REDDIT_BUCKET_NAME: 'reddit'
}

@appends_bp.route("/files", methods=["POST"])
def append_object_files():
    try:
        data = request.get_json()
        validate_request_data(data, ["objectURLs", "exportFormat"])
        object_urls = data.get("objectURLs")
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
        combined_sheet_data = {}
        for url in object_urls:
            parsed_url = urlparse(url)
            # Extract the bucket name
            bucket_name = parsed_url.netloc.split('.')[0]
            file_name = os.path.basename(parsed_url.path)
            try:
                sheet_data = s3_manager.retrieve_dataFrames_from_sheets(file_name, bucket_name, export_format.value)
            except ValueError as e:
                print(f"Skipping URL '{url}' - {e}")
                continue
            for sheet_name, df in sheet_data:
                prefix = bucket_name_prefixes.get(bucket_name, '')
                modified_sheet_name = f'{prefix}_{sheet_name}' if prefix else sheet_name
                combined_sheet_data[modified_sheet_name] = df

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"consolidate_{timestamp}"
        object_url = s3_manager.store_dataFrame_to_sheet(
            Config.CONSOLIDATE_BUCKET_NAME, file_name, export_format.value, combined_sheet_data
        )
        return create_response(
            status=True, data={"objectURL": object_url}
        )
    except ValueError as e:
        print(f"operation failed due to {e}")
        return create_response(
            status=False,
            error="failed due to generic server error",
            status_code=500,
            error_code=ErrorCodes.GENERIC_SERVER_ERROR,
        )

