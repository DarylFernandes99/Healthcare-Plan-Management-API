import pika
import json
import os
import threading
from src import plan_model, config
import logging

logger = logging.getLogger(__name__)

class RabbitMQConsumer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config.RABBITMQ_HOST, port=config.RABBITMQ_PORT)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='plans')
    
    def process_message_callback(self, plan_data):
        logger.info("Processing plan data")
        # Implement your logic here
        if plan_data['action'] == 'create':
            logger.info("Creating plan in Redis and ElasticSearch")
            plan_model.create_plan(plan_data['data'])
        elif plan_data['action'] == 'update':
            logger.info("Updating plan in Redis and ElasticSearch")
            plan_model.update_plan_partial(plan_data['data']['objectId'], plan_data['data'])
    
    def run(self):
        def callback(ch, method, properties, body):
            logger.info("Queued plan data")
            plan_data = json.loads(body)
            try:
                self.process_message_callback(plan_data)
            except Exception as e:
                logger.error(str(e))
            finally:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info("Queued item processing completed")

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='plans', on_message_callback=callback)

        logger.info('RabbitMQ is ready')
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()
