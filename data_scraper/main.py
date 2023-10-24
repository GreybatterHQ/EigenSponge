from amazon_scraper import AmazonScraper
from reddit_scraper import reddit_scraper
from instagram_scraper import instagram_scraper

def main():
    amazon = AmazonScraper("https://scrape.smartproxy.com/v1/tasks", "config_2.json")
    amazon.scrape_amazon_data()
    instagram_scraper()
    reddit_scraper()

main()