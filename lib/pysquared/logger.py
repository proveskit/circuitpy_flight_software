"""
Logger class for handling logging messages with different severity levels.
Logs can be output to standard output or saved to a file (functionality to be implemented).
"""

# NVM register number
import json
import time

from lib.pysquared.nvm.counter import Counter
from lib.pysquared.nvm.registers import ERRORCNT

try:
    from stubs.circuitpython.byte_array import ByteArray
except ImportError:
    pass


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
        datastore: ByteArray,
        log_level: int = LogLevel.DEBUG,
        log_mode: int = LogMode.PRINT,
    ) -> None:
        # mapping each level to a numerical value. Used to help support log_level.
        # If log function used is equal to or above the value, it can be used
        self.datastore: ByteArray = datastore
        self.logToStandardOut: bool = True
        self.error_count: Counter = Counter(index=ERRORCNT, datastore=self.datastore)
        self.log_level: int = log_level
        self.log_mode: int = log_mode

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

        if self.logToStandardOut and self.can_print_this_level(level_value):
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
        self.error_count.increment()
        self._log("ERROR", 4, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level CRITICAL.
        """
        self._log("CRITICAL", 5, message, **kwargs)

    def get_error_count(self) -> int:
        return self.error_count
