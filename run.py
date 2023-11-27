from app import create_app
from app.config import Config

app = create_app()

app.config.from_object(Config)

if __name__ == "__main__":
    app.run(debug=True, port=Config.APP_PORT)
