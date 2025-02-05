"""
Logger class for handling logging messages with different severity levels.
Logs can be output to standard output or saved to a file (functionality to be implemented).
"""

import json
import time
from collections import OrderedDict

from lib.pysquared.debugcolor import co
from lib.pysquared.nvm.counter import Counter


class LogLevel:
    NOTSET = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


LEVEL_COLORS = {
    "DEBUG": "blue",
    "INFO": "white",
    "WARNING": "orange",
    "ERROR": "red",
    "CRITICAL": "red",
}


class Logger:
    def __init__(
        self,
        error_counter: Counter,
        log_level: int = LogLevel.NOTSET,
        colorize: bool = False,
    ) -> None:
        self._error_counter: Counter = error_counter
        self._log_level: int = log_level
        self._colorize: bool = colorize

    def _can_print_this_level(self, level_value: int) -> bool:
        return level_value >= self._log_level

    def _log(self, level: str, level_value: int, message: str, **kwargs) -> None:
        """
        Log a message with a given severity level and any addional key/values.
        """
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"

        # Create ordered dictionary with desired field order
        ordered_output = OrderedDict()
        ordered_output["time"] = asctime
        ordered_output["level"] = level
        ordered_output["msg"] = message

        # Add any additional kwargs after the required fields
        ordered_output.update(kwargs)

        json_output = json.dumps(ordered_output)

        if self._can_print_this_level(level_value):
            if self._colorize:
                # Replace the plain level string with colored version after JSON serialization
                json_output = json_output.replace(
                    f'"{level}"', f'"{co(level, color=LEVEL_COLORS[level])}"'
                )
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
        return self._error_counter.get()
