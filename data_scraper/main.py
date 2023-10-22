from amazon_scraper import scrape_amazon_data
from reddit_scraper import reddit_scraper
from instagram_scraper import instagram_scraper

def main():
    scrape_amazon_data()
    instagram_scraper()
    reddit_scraper()

main()