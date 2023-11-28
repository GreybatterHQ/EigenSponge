import pandas as pd
import json
from utils.http_utils import request_handler
from app.enums.sheet_names import SheetName


class RedditScraper:
    header = {}

    def __init__(self, url, auth_token):
        self.url = url
        self.init_api_auth(auth_token)
        self.posts_df = pd.DataFrame()
        self.users_df = pd.DataFrame()

    def init_api_auth(self, auth_token):
        self.header = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {auth_token}",
        }

    def scrape_post_data(self, post_url):
        payload = {
            "target": "reddit_post",
            "url": post_url,
            "locale": " en-us",
            "geo": "United States",
        }
        try:
            response_json = request_handler(self.url, "POST", payload, self.header)
        except Exception as e:
            print(f"An error occurred while fetching post data {e}")
            return
        print(response_json)
        # posts = response_json
        # self.posts_df = self.posts_df.append(pd.DataFrame(posts))

    def scrape_subreddit_data(self, subreddit_name):
        subreddit_url = f"https://www.reddit.com/r/{subreddit_name}/"
        payload = {
            "target": "reddit_subreddit",
            "url": subreddit_url,
        }
        subreddit_df = pd.DataFrame()
        authors = set()
        try:
            response_json = request_handler(self.url, "POST", payload, self.header)
            posts = response_json["results"][0]["content"]["data"]["children"]
            subreddit_data = []
            for post in posts:
                subreddit_data.append(
                    {
                        "title": post["data"]["title"],
                        "permalink": f"https://www.reddit.com{post['data']['permalink']}",
                        "url": post["data"]["url"],
                        "author": post["data"]["author"],
                        "isVideo": post["data"]["is_video"],
                        "ups": post["data"]["ups"],
                        "subreddit": post["data"]["subreddit"],
                        "over_18": post["data"]["over_18"],
                    }
                )
                authors.add(post["data"]["author"])

            subreddit_df = subreddit_df.append(pd.DataFrame(subreddit_data))
            return authors, subreddit_df 
        except Exception as e:
            print(f"An error occurred while fetching subreddit data {e}")
            return

    def scrape_users_data(self, user_profile_url):
        payload = {
            "target": "reddit_user",
            "url": f"https://www.reddit.com/user/{user_profile_url}",
        }
        try:
            response_json = request_handler(self.url, "POST", payload, self.header)
            user_posts = response_json["results"][0]["content"]["data"]["children"]
            data = []
            for post in user_posts:
                awarders = post["data"]["awarders"] or None
                if post["kind"] == "t3":
                    data.append(
                        {
                            "type": "post",
                            "id": post["data"]["id"],
                            "title": post["data"]["title"],
                            "permalink": f"https://www.reddit.com{post['data']['permalink']}",
                            "author": post["data"]["author"],
                            "url": post["data"]["url"],
                            "subreddit_subscribers": post["data"][
                                "subreddit_subscribers"
                            ],
                            "over_18": post["data"]["over_18"],
                            "ups": post["data"]["ups"],
                            "awarders": awarders,
                            "body": None,
                            "replies": None,
                            "created": post["data"]["created_utc"],
                            "subreddit": post["data"]["subreddit"],
                        }
                    )
                elif post["kind"] == "t1":
                    data.append(
                        {
                            "type": "comment",
                            "id": post["data"]["id"],
                            "title": post["data"]["link_title"],
                            "permalink": f"https://www.reddit.com{post['data']['permalink']}",
                            "author": post["data"]["author"],
                            "url": None,
                            "subreddit_subscribers": None,
                            "over_18": post["data"]["over_18"],
                            "ups": post["data"]["ups"],
                            "awarders": awarders,
                            "body": post["data"]["body"],
                            "replies": post["data"]["replies"],
                            "created": post["data"]["created_utc"],
                            "subreddit": post["data"]["subreddit"],
                        }
                    )

            self.users_df = self.users_df.append(pd.DataFrame(data))
        except Exception as e:
            print(f"An error occurred while fetching user data {e}")
            return

    def scrape_data(self, subreddit_name):
        authors, subreddit_df = self.scrape_subreddit_data(subreddit_name)
        print(f"data for subreddit {subreddit_name} scrapped successfully")
        for author in list(authors):
            self.scrape_users_data(author)
            print(f"data for reddit user {author} scraped successfully")

        return [
            (SheetName.SUBREDDIT_POST.value, subreddit_df),
            (SheetName.USERS_DATA.value, self.users_df)
        ]
