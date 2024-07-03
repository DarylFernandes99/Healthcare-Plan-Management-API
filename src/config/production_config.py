import os
import logging
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

class ProductionConfig:
    def __init__(self):
        self.ENV = "production"
        self.DEBUG = False
        self.PORT = os.environ.get('PROD_PORT')
        self.HOST = os.environ.get('PROD_HOST')
        self.LOG_LEVEL = logging.INFO
        self.REDIS_HOST = os.environ.get('REDIS_PROD_HOST')
        self.REDIS_PORT = os.environ.get('REDIS_PROD_PORT')
        self.VERSION = os.environ.get('PROD_VERSION')
        self.OAUTH_CLIENT_ID = os.environ.get('DEV_OAUTH_CLIENT_ID')
