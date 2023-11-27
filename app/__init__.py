from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes.amazon_routes import amazon_bp
    app.register_blueprint(amazon_bp, url_prefix='/data-scraper/api/v1/amazon')

    # Add more blueprints or configurations as needed
    return app
