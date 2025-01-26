"""
Logger class for handling logging messages with different severity levels.
Logs can be output to standard output or saved to a file (functionality to be implemented).
"""

import json
import time

import microcontroller
from micropython import const

from lib.pysquared.nvm.counter import Counter

# NVM register number
_ERRORCNT = const(7)


class Logger:
    def __init__(self, log_level: str = "DEBUG", log_mode: str = "PRINT") -> None:
        # mapping each level to a numerical value. Used to help support log_level.
        # If log function used is equal to or above the value, it can be used
        self.levels_map: dict = {
            "NOTSET": 0,
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }
        self.log_modes_set: set = {"PRINT", "FILE", "BOTH"}
        self.logToStandardOut: bool = True
        self.error_count: Counter = Counter(
            index=_ERRORCNT, datastore=microcontroller.nvm
        )
        self.log_level: str = self.parse_log_level(log_level)
        self.log_mode: str = self.parse_log_mode(log_mode)

    def parse_log_level(self, log_level: str) -> str:
        """
        Parses the log_level entered into the config.json
        """
        log_level: str = log_level.upper()
        log_level: str = log_level.strip()

        # function returns DEBUG as the log_level if an invalid log_level is entered
        if log_level not in self.levels_map:
            log_level: str = "DEBUG"

        return log_level

    def parse_log_mode(self, log_mode: str) -> str:
        """
        Parses the log_mode entered into the config.json
        """
        log_mode: str = log_mode.upper()
        log_mode: str = log_mode.strip()

        # function returns PRINT as the log_mode if an invalid mode is entered
        if log_mode not in self.log_modes_set:
            log_mode: str = "PRINT"

        return log_mode

    def can_print_this_level(self, level: str) -> bool:
        return self.levels_map[level] >= self.levels_map[self.log_level]

    def _log(self, level: str, message: str, **kwargs) -> None:
        """
        Log a message with a given severity level and any addional key/values.
        """
        kwargs["level"] = level
        kwargs["msg"] = message

        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime

        json_output = json.dumps(kwargs)

        if self.logToStandardOut and self.can_print_this_level(level):
            print(json_output)

    def debug(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level DEBUG.
        """
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level INFO.
        """
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level WARNING.
        """
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level ERROR.
        """
        self.error_count.increment()
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level CRITICAL.
        """
        self._log("CRITICAL", message, **kwargs)

    def get_error_count(self) -> int:
        return self.error_count
