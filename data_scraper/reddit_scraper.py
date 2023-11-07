import __init__
import pandas as pd
import json
from utils.http_utils import request_handler
from utils.excel_utils import save_dataFrame_to_excel

class RedditScraper:
    header = {}
    file_name = 'reddit_output.xlsx'
    output_directory = 'output'
    authors = set()

    def __init__(self, url, config_path):
        self.url = url
        self.init_api_auth(config_path)
        self.posts_df = pd.DataFrame()
        self.subreddit_df = pd.DataFrame()
        self.users_df = pd.DataFrame()

    def init_api_auth(self, config_path):
        with open(config_path,"r") as config_file:
            config = json.load(config_file)
        self.header = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Basic "+ config['social_media_auth_token']
        }

    def scrape_post_data(self, post_url):
        payload = {
            "target": "reddit_post",
            "url": post_url,
            "locale": " en-us",
            "geo": "United States"
        }
        try:
            response_json = request_handler(self.url, 'POST', payload, self.header)
        except Exception as e:
            print(f'An error occurred while fetching post data {e}')
            return
        print(response_json)
        # posts = response_json
        # self.posts_df = self.posts_df.append(pd.DataFrame(posts))

    def scrape_subreddit_data(self, subreddit_url):
        payload = {
            "target": "reddit_subreddit",
            "url": subreddit_url,
        }
        try:
            response_json = request_handler(self.url, 'POST', payload, self.header)
            posts = response_json['results'][0]['content']['data']['children']
            subreddit_data = []
            for post in posts:
                subreddit_data.append({
                'title': post['data']['title'],
                'permalink': f"https://www.reddit.com{post['data']['permalink']}",
                'url': post['data']['url'],
                'author': post['data']['author'],
                'isVideo': post['data']['is_video'],
                'ups': post['data']['ups'],
                'subreddit': post['data']['subreddit'],
                'over_18': post['data']['over_18']
                })
                self.authors.add(post['data']['author'])

            self.subreddit_df = self.subreddit_df.append(pd.DataFrame(subreddit_data))
        except Exception as e:
            print(f'An error occurred while fetching subreddit data {e}')
            return
    
    def scrape_users_data(self, user_profile_url):
        payload = {
            "target": "reddit_user",
            "url": f'https://www.reddit.com/user/{user_profile_url}',
        }
        try:
            response_json = request_handler(self.url, 'POST', payload, self.header)
            user_posts = response_json['results'][0]['content']['data']['children']
            data = []
            for post in user_posts:
                awarders = post['data']['awarders'] if post['data']['awarders'] else None
                if post['kind'] == 't3':
                    data.append({
                        'type': 'post',
                        'id': post['data']['id'],
                        'title': post['data']['title'],
                        'permalink': f"https://www.reddit.com{post['data']['permalink']}",
                        'author': post['data']['author'],
                        'url': post['data']['url'],
                        'subreddit_subscribers': post['data']['subreddit_subscribers'],
                        'over_18': post['data']['over_18'],
                        'ups': post['data']['ups'],
                        'awarders': awarders,
                        'body': None,
                        'replies': None,
                        'created': post['data']['created_utc'],
                        'subreddit': post['data']['subreddit']
                    })
                elif post['kind'] == 't1':
                    data.append({
                        'type': 'comment',
                        'id': post['data']['id'],
                        'title': post['data']['link_title'],
                        'permalink': f"https://www.reddit.com{post['data']['permalink']}",
                        'author': post['data']['author'],
                        'url': None,
                        'subreddit_subscribers': None,
                        'over_18': post['data']['over_18'],
                        'ups': post['data']['ups'],
                        'awarders': awarders,
                        'body': post['data']['body'],
                        'replies': post['data']['replies'],
                        'created': post['data']['created_utc'],
                        'subreddit': post['data']['subreddit']
                    })

            self.users_df = self.users_df.append(pd.DataFrame(data))
        except Exception as e:
            print(f'An error occurred while fetching user data {e}')
            return
    

    def scrape_data(self, input_file):
        print('initialized reddit scraper')
        try:
            reddit_input = pd.read_excel(input_file)
            print(f'successfully loaded input file {input_file}')
        except FileNotFoundError:
            print('input file not found')
            exit()

        for row in reddit_input.itertuples():
            self.scrape_subreddit_data(row[1])
            print(f'data for subreddit {row[1]} scrapped successfully')
        save_dataFrame_to_excel(self.file_name, 'subreddit_posts', self.subreddit_df, self.output_directory)
        print('all unique authors are:', list(self.authors))

        for author in list(self.authors):
            self.scrape_users_data(author)
        save_dataFrame_to_excel(self.file_name, 'users_data', self.users_df, self.output_directory)