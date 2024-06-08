from src import config, app

if __name__ == "__main__":
    app.logger.info("Server started running at {}:{}".format(config.HOST, config.PORT))
    app.run(host= config.HOST,
        port= config.PORT,
        debug= config.DEBUG)
    app.logger.info("Server terminated at {}:{}".format(config.HOST, config.PORT))
