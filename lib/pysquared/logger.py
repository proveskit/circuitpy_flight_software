"""
Logger class for handling logging messages with different severity levels.
Logs can be output to standard output or saved to a file (functionality to be implemented).
"""

import json
import time

from lib.pysquared.nvm.counter import Counter


class LogMode:
    PRINT = 1
    FILE = 2
    BOTH = 3


class LogLevel:
    NOTSET = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class Logger:
    def __init__(
        self,
        error_counter: Counter,
        log_level: int = LogLevel.NOTSET,
    ) -> None:
        self._error_counter: Counter = error_counter
        self._log_level: int = log_level

    def can_print_this_level(self, level_value: int) -> bool:
        return level_value >= self.log_level

    def _log(self, level: str, level_value: int, message: str, **kwargs) -> None:
        """
        Log a message with a given severity level and any addional key/values.
        """
        kwargs["level"] = level
        kwargs["msg"] = message

        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime

        json_output = json.dumps(kwargs)

        if self.log_to_standard_out and self.can_print_this_level(level_value):
            print(json_output)

    def debug(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level DEBUG.
        """
        self._log("DEBUG", 1, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level INFO.
        """
        self._log("INFO", 2, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level WARNING.
        """
        self._log("WARNING", 3, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level ERROR.
        """
        self._error_counter.increment()
        self._log("ERROR", 4, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level CRITICAL.
        """
        self._log("CRITICAL", 5, message, **kwargs)

    def get_error_count(self) -> int:
        return self.error_counter.get()
