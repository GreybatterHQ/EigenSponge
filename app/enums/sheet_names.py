from enum import Enum


class SheetName(Enum):
    # Amazon
    PAID = "paid"
    ORGANIC = "organic"
    AMAZON_CHOICES = "amazon_choices"
    REVIEWS = "reviews"
    PRICING = "pricing"
    PRODUCTS = "products"
    QUESTIONS = "questions"
    # Reddit
    SUBREDDIT_POST = "subreddit_posts"
    USERS_DATA = "users_data"
    # Instagram
    INSTAGRAM_POSTS = "posts"
    INSTAGRAM_USER_DATA = "user_data"
    INSTAGRAM_USER_POSTS = "user_posts"
