from app import create_app
from app.config import Config, Environment

app = create_app()

app.config.from_object(Config)

if __name__ == "__main__":
    debug_flag = Config.ENVIRONMENT != Environment.PRODUCTION.value
    app.run(host='0.0.0.0', debug=debug_flag, port=Config.APP_PORT)
