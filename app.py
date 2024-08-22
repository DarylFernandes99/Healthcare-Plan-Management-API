import threading
from src import config, app
from src.consumer import RabbitMQConsumer

consumer = RabbitMQConsumer()

if __name__ == "__main__":
    app.logger.info("Server started running at {}:{}".format(config.HOST, config.PORT))
    
    with app.app_context():
        try:
            consumer.start()
            app.run(
                host=config.HOST,
                port=config.PORT,
                debug=config.DEBUG,
                # ssl_context="adhoc"
            )
        except Exception as e:
            app.logger.error(str(e))
        finally:
            app.logger.info("Server terminated at {}:{}".format(config.HOST, config.PORT))
            consumer.stop()
