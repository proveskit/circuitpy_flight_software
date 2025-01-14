import json
import time

# from adafruit_blinka import Enum
import adafruit_logging as logging

# class DebugMode(Enum):
# PRINTMODE = False
# DEBUGMODE = True


class Logger:
    def __init__(self):
        # self.debugmode = DebugMode.DEBUGMODE
        self.internal_logger = logging.getLogger("logger")
        self.internal_logger.setLevel(logging.DEBUG)

    def setPrintMode(self):
        # self.debugmode = DebugMode.PRINTMODE
        pass

    def setDebugMode(self):
        # self.debugmode = DebugMode.DEBUGMODE
        pass

    def debug(self, filename, message, **kwargs):
        # logging.basicConfig(level=logging.INFO, format='%(message)s')
        # full_message = "[" + filename + "]" + message
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["message"] = message
        kwargs["level"] = "DEBUG"
        json_output = json.dumps(kwargs)
        print(json_output)

    def info(self, filename, **kwargs):
        # self.internal_logger.info(message, *args)
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "INFO"
        json_output = json.dumps(kwargs)
        print(json_output)

    def warning(self, message, *args):
        self.internal_logger.warning(message, *args)

    def error(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "ERROR"
        json_output = json.dumps(kwargs)
        print(json_output)

    def critical(self, message, *args):
        self.internal_logger.critical(message, *args)
