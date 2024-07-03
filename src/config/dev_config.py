import os
import logging
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

class DevConfig:
    def __init__(self):
        self.ENV = "development"
        self.DEBUG = True
        self.PORT = os.environ.get('DEV_PORT')
        self.HOST = os.environ.get('DEV_HOST')
        self.LOG_LEVEL = logging.DEBUG
        self.REDIS_HOST = os.environ.get('REDIS_DEV_HOST')
        self.REDIS_PORT = os.environ.get('REDIS_DEV_PORT')
        self.VERSION = os.environ.get('DEV_VERSION')
        self.OAUTH_CLIENT_ID = os.environ.get('DEV_OAUTH_CLIENT_ID')
