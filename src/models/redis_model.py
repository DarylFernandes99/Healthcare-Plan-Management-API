import json
import logging
from redis import Redis

logger = logging.getLogger(__name__)

class RedisModel:
    def __init__(self, redis_client: Redis, key_prefix: str):
        self.redis_client = redis_client
        self.key_prefix = key_prefix

    def get_key(self, id):
        return f"{self.key_prefix}:{id}"

    def save(self, id, data):
        key = self.get_key(id)
        self.redis_client.set(key, json.dumps(data))
        logger.info("Save data to redis - {}".format(key))

    def get(self, id):
        key = self.get_key(id)
        data = self.redis_client.get(key)
        if data:
            logger.info("Fetched data from redis - {}".format(key))
            return json.loads(data)
        logger.info("Failed to get data from redis - {}".format(key))
        return None
    
    def check_key_exists(self, id):
        key = self.get_key(id)
        logger.info("Check key exists in redis - {}".format(key))
        return self.redis_client.exists(key)

    def delete(self, id):
        key = self.get_key(id)
        val = self.redis_client.delete(key)
        logger.info("Key deleted from redis - {}".format(key))
        return val
