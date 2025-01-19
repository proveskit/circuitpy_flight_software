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
        self.logToFile = False
        self.logToStandardOut = True

    # @blakejameson NOTE: functionality to save logs to file will be implemented at a later point. For now, logs will
    # be output to standard output
    # def saveLogToFile():
    #    pass

    def setLogToFile(self):
        self.logToFile = True
        self.logToStandardOut = False

    def setLogToStdOut(self):
        self.logToStandardOut = True
        self.logToFile = False

    def debug(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "DEBUG"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)

        if self.logToStandardOut:
            print(json_output)

    def info(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "INFO"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)

        if self.logToStandardOut:
            print(json_output)

    def warning(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "WARNING"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)

        if self.logToStandardOut:
            print(json_output)

    def error(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "ERROR"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)

        if self.logToStandardOut:
            print(json_output)

    def critical(self, filename, **kwargs):
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        kwargs["level"] = "CRITICAL"
        kwargs["file"] = filename
        json_output = json.dumps(kwargs)

        if self.logToStandardOut:
            print(json_output)
