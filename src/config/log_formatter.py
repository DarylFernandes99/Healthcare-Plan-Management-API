import json

class LogFormatter():
    def custom_formatter(record):
        # escaped_message = record.getMessage().replace('"', '\"')
        log_entry = {
            "timestamp": record.asctime,
            "level": record.levelname,
            "logger": record.module,
            "message": record.getMessage()
        }
        return json.dumps(log_entry)
