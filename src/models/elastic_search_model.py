import json
from elasticsearch import Elasticsearch
from src import config
import logging

logger = logging.getLogger(__name__)

class ElasticSearchConfig:
    def __init__(self):
        self.conn = self.connect_elasticsearch()

    def connect_elasticsearch(self, **kwargs):
        _es_config = config.ELASTIC_HOST
        _es_hosts = [_es_config]
        if 'hosts' in kwargs.keys():
            _es_hosts = kwargs['hosts']
        _es_obj = None
        _es_obj = Elasticsearch(hosts=_es_hosts, timeout=10)

        if _es_obj.ping():
            logger.info("Connection to ElasticSearch successfull")

            # Create indices
            INDEX_NAME = "plans"
            mappings = json.load(open("src/models/planMappings.json"))

            try:
                if not _es_obj.indices.exists(INDEX_NAME):
                    _es_obj.indices.create(index=INDEX_NAME, body=mappings)
                    logger.info("Indices created successfully")
                    return
                logger.info("Indices already exists")
            except Exception as e:
                logger.error("{}".format(str(e)))
        else:
            logger.error("Could not connect to ElasticSearch")
        
        return _es_obj
    
    def bulk_operations(self, data):
        try:
            self.conn.bulk(data)
            logger.info("Bulk operations completed successfully")
        except Exception as e:
            logger.error(str(e))
    
    def create_index(self, **kwargs):
        try:
            self.conn.index(**kwargs)
            logger.info("Created index with id -> {}".format(kwargs.get("id", "None")))
        except Exception as e:
            logger.error(str(e))
    
    def update_index(self, **kwargs):
        try:
            kwargs["body"] = {
                "doc": kwargs.get("body"),
                "doc_as_upsert" : True
            }
            self.conn.update(**kwargs)
            logger.info("Updated index with id -> {}".format(kwargs.get("id", "None")))
        except Exception as e:
            logger.error(str(e))
    
    def search_index(self, **kwargs):
        data = None
        try:
            data = self.conn.search(**kwargs)
            logger.info("Found index")
        except Exception as e:
            logger.error(str(e))

        return data
