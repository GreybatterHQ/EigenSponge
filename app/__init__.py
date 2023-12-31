from flask import Flask
from app.routes.amazon_routes import amazon_bp
from app.routes.reddit_routes import reddit_bp
from app.routes.instagram_routes import instagram_bp
from app.routes.appends_routes import appends_bp

def create_app():
    app = Flask(__name__)

    blueprints = [amazon_bp, reddit_bp, instagram_bp, appends_bp]
    for blueprint in blueprints:
        app.register_blueprint(
            blueprint, url_prefix=f"/data-scraper/api/{blueprint.name}"
        )
    return app
