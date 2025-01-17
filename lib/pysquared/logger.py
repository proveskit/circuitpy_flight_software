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

    def debug(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "DEBUG"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)
        print(json_output)

    def info(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "INFO"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)
        print(json_output)

    def warning(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "WARNING"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)
        print(json_output)

    def error(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "ERROR"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)
        print(json_output)

    def critical(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "CRITICAL"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)
        print(json_output)
