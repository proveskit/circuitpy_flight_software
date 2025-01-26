"""
Logger class for handling logging messages with different severity levels.
Logs can be output to standard output or saved to a file (functionality to be implemented).
"""

import json
import time


class Logger:
    def __init__(self, log_level: str, log_mode: str) -> None:
        self.logToStandardOut: bool = True
        self.error_count: int = 0
        self.log_level: str = log_level
        self.log_mode: str = log_mode

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

        if self.logToStandardOut:
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
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """
        Log a message with severity level CRITICAL.
        """
        self._log("CRITICAL", message, **kwargs)

    def increment_error(self) -> None:
        self.error_count += 1
