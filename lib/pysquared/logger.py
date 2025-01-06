import adafruit_logging as logging


class Logger:

    def __init__(self):
        self.internal_logger = logging.getLogger("logger")
        self.internal_logger.setLevel(logging.DEBUG)

    def log(self, message):
        self.internal_logger.debug(message)
