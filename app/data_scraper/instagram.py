import pandas as pd
from utils.http_utils import request_handler
from app.enums.sheet_names import SheetName


class InstagramScraper:
    header = {}

    def __init__(self, url, auth_token):
        self.url = url
        self.header = self.init_api_auth(auth_token)

    def init_api_auth(self, auth_token):
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {auth_token}",
        }

    def scrape_hashtag_data(self, hashtag):
        payload = {
            "target": "instagram_graphql_hashtags",
            "query": hashtag,
        }
        try:
            print(f"scraping data for hashtag {hashtag}")
            response_json = request_handler(self.url, "POST", payload, self.header)
        except Exception as e:
            print(f"An error occurred while fetching hashtag data {e}")
            return SheetName.INSTAGRAM_POSTS.value, pd.DataFrame()
        hashtag_info = response_json["results"][0]["content"]["data"]["hashtag"]
        # Check if the hashtag data is present or not
        if hashtag_info is None:
            print(f'no content found for the hashtag {hashtag}')
            return SheetName.INSTAGRAM_POSTS.value, pd.DataFrame()
        hashtag_name = hashtag_info["name"]
        posts = hashtag_info["edge_hashtag_to_media"]["edges"]

        # Creating lists using list comprehension
        post_details = [
            {
                "id": post["node"]["id"],
                "text": post["node"]["edge_media_to_caption"]["edges"][0]["node"][
                    "text"
                ],
                "shortcode": post["node"]["shortcode"],
                "timestamp": post["node"]["taken_at_timestamp"],
                "image_url": post["node"]["display_url"],
                "is_video": post["node"]["is_video"],
                "dimension": f"{post['node']['dimensions']['width']} x {post['node']['dimensions']['height']}",
                "hashtag": hashtag_name,
                "user": post["node"]["owner"]["id"],
            }
            for post in posts
        ]
        print(f"successfully fetched data for hashtag {hashtag}")

        return SheetName.INSTAGRAM_POSTS.value, pd.DataFrame(post_details)

    def scrape_user_data(self, profile):
        payload = {
            "url": f"https://www.instagram.com/{profile}",
            "target": "instagram_profile",
        }
        try:
            response_json = request_handler(self.url, "POST", payload, self.header)
        except Exception as e:
            raise ValueError(
                f"An error occurred while fetching user profile data for {profile}: {e}"
            ) from e
        user_data = response_json["results"][0]["content"]["account"]
        if user_data["username"] == "":
            raise ValueError(f'user {profile} does not exist')

        stats = response_json["results"][0]["content"]["stats"]
        posts = response_json["results"][0]["content"]["posts"]

        user_df = pd.DataFrame(
            [
                {
                    "username": user_data["username"],
                    "verified": user_data["verified"],
                    "posts": stats["posts"],
                    "followers": stats["followers"],
                    "following": stats["following"],
                }
            ]
        )
        print(f'user data fetched for instagram user {profile}')
        user_posts_df = pd.DataFrame()
        for post in posts:
            user_posts_df = user_posts_df.append(
                pd.DataFrame(
                    [
                        {
                            "username": user_data["username"],
                            "post URL": post["href"],
                            "post description": post["description"],
                        }
                    ]
                )
            )
        print(f'user posts data fetched for instagram user {profile}')
        return [
            (SheetName.INSTAGRAM_USER_DATA.value, user_df),
            (SheetName.INSTAGRAM_USER_POSTS.value, user_posts_df),
        ]
