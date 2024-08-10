from flask import Flask
from flask_cors import CORS
import os
from src.config.config import Config
from src.config.log_formatter import LogFormatter
from dotenv import load_dotenv
import logging
from redis import Redis
from flask_swagger_ui import get_swaggerui_blueprint

# Logger
logger = logging.getLogger(__name__)

# loading environment variables
load_dotenv()

# declaring flask application
app = Flask(__name__, static_url_path='/static', static_folder='../static')

# Setting up CORS
CORS(app)

# calling the dev configuration
config = Config().production_config if os.environ.get("PYTHON_ENV") == "production" else Config().dev_config

# making our application to use env
app.env = config.ENV

# Configure Flask logging
app.logger.setLevel(config.LOG_LEVEL)  # Set log level to INFO
logger_path = "./logs"
if not os.path.exists(logger_path):
    os.makedirs(logger_path)
handler = logging.FileHandler(logger_path + "/logfile.log")  # Log to a file
# adding timestamp formatter
formatter = logging.Formatter('{"timestamp":"%(asctime)s", "level":"%(levelname)s", "logger":"%(module)s", "message":"%(message)s"}')
handler.setFormatter(formatter)
handler.format = LogFormatter.custom_formatter
app.logger.addHandler(handler)

# import plans model
from src.models.plans_model import PlanModel
from src.models.elastic_search_model import ElasticSearchConfig
redis_client_plan = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
es_config = ElasticSearchConfig()
plan_model = PlanModel(redis_client_plan, es_config)
logger.info("Created plan model")

from src.models.etag_model import EtagModel
redis_client_etag = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
etag_model = EtagModel(redis_client_etag)
logger.info("Created etag model")

# import api blueprint to register it with app
from src.routes import api
app.register_blueprint(api, url_prefix = "/")

# Creating swagger documentation of APIs
SWAGGER_URL="/docs"
API_URL="/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Adv Big-Data App/Indexing'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
