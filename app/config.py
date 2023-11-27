# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # App config
    APP_PORT = int(os.getenv("PORT", default=5001))
    # AWS credentials
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AMAZON_BUCKET_NAME = os.getenv("AMAZON_BUCKET_NAME")
    REGION_NAME = os.getenv("REGION_NAME")
    # SmartProxy Keys
    SCRAPE_BASE_URL = os.getenv("SCRAPE_BASE_URL")
    API_BASIC_AUTH_TOKEN = os.getenv("API_BASIC_AUTH_TOKEN")
    SOCIAL_MEDIA_AUTH_TOKEN = os.getenv("SOCIAL_MEDIA_AUTH_TOKEN")
    required_keys = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AMAZON_BUCKET_NAME",
        "SCRAPE_BASE_URL",
        "API_BASIC_AUTH_TOKEN",
        "SOCIAL_MEDIA_AUTH_TOKEN"
    ]

    if missing_keys := [key for key in required_keys if not os.getenv(key)]:
        missing_keys_str = ", ".join(missing_keys)
        raise ValueError(
            f"Environment variables are not set. Set environment variables: {missing_keys_str}."
        )
