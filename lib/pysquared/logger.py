"""
Logger class for handling logging messages with different severity levels.
Logs can be output to standard output or saved to a file (functionality to be implemented).
"""

import json
import time

# from adafruit_blinka import Enum

# class DebugMode(Enum):
# PRINTMODE = False
# DEBUGMODE = True


class Logger:
    # def __init__(self):
    #     self.debugmode = DebugMode.DEBUGMODE
    #     self.logToFile = False
    #     self.logToStandardOut = True

    # @blakejameson NOTE: functionality to save logs to file will be implemented at a later point. For now, logs will
    # be output to standard output
    # def saveLogToFile():
    #    pass

    # def setLogToFile(self):
    #     """
    #     Set the logger to save logs to a file.
    #     """
    #     self.logToFile = True
    #     self.logToStandardOut = False

    # def setLogToStdOut(self):
    #     """
    #     Set the logger to output logs to standard output.
    #     """
    #     self.logToStandardOut = True
    #     self.logToFile = False

    def _log(self, level: str, message: str, **kwargs):
        """
        Log a message with a given severity level and any addional key/values.
        """
        kwargs["level"] = level
        kwargs["msg"] = message

        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime

        json_output = json.dumps(kwargs)

        if self.logToStandardOut:
            print(json_output)

    def debug(self, message: str, **kwargs):
        """
        Log a message with severity level DEBUG.
        """
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        """
        Log a message with severity level INFO.
        """
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """
        Log a message with severity level WARNING.
        """
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        """
        Log a message with severity level ERROR.
        """
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs):
        """
        Log a message with severity level CRITICAL.
        """
        self._log("CRITICAL", message, **kwargs)
