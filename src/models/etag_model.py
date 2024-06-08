import json
from redis import Redis
from src.models.redis_model import RedisModel

class EtagModel(RedisModel):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client, "etag")
    
    def save_etag(self, etag_value, plan_data):
        return self.save(etag_value, plan_data)
    
    def get_etag(self, etag_value):
        return self.get(etag_value)
