from amazon_scraper import AmazonScraper
from reddit_scraper import RedditScraper
from instagram_scraper import InstagramScraper

def main():
    amazon = AmazonScraper("https://scrape.smartproxy.com/v1/tasks", "config_2.json")
    amazon.scrape_amazon_data('input_amazon_search.xlsx', 'input_amazon_product.xlsx')

    instagram = InstagramScraper("https://scraper-api.smartproxy.com/v2/scrape", "config_2.json")
    instagram.scrape_data()

    reddit = RedditScraper("https://scraper-api.smartproxy.com/v2/scrape", "config_2.json")
    reddit.scrape_data("reddit_input_sheet.xlsx")

main()