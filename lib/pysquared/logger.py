import adafruit_logging as logging


class Logger:

    def __init__(self):
        self.internal_logger = logging.getLogger("logger")
        self.internal_logger.setLevel(logging.DEBUG)

    def log(self, filename, message, *args):
        full_message = "[" + filename + "]" + message
        self.internal_logger.debug(full_message, *args)

    def info(self, message, *args):
        self.internal_logger.info(message, *args)

    def warning(self, message, *args):
        self.internal_logger.warning(message, *args)

    def error(self, message, *args):
        self.internal_logger.error(message, *args)

    def critical(self, message, *args):
        self.internal_logger.critical(message, *args)
