import json
import time
import traceback

from lib.pysquared.nvm.counter import Counter


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

    def _can_print_this_level(self, level_value: int) -> bool:
        return level_value >= self._log_level

    def _log(self, level: str, level_value: int, message: str, **kwargs) -> None:
        """
        Log a message with a given severity level and any additional key/values.
        """

        # Manually format the time since time.strftime is not available in CircuitPython
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime

        # case where someone used debug, info, or warning yet also provides an 'err' kwarg with an Exception
        if (
            "err" in kwargs
            and level not in ("ERROR", "CRITICAL")
            and isinstance(kwargs["err"], Exception)
        ):
            kwargs["err"] = traceback.format_exception(kwargs["err"])

        json_output = json.dumps(kwargs)

        if self._can_print_this_level(level_value):
            print(json_output)
        if self.log_file:
            self.log_file.write(json_output + "\n")
            self.log_file.flush()

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

    def error(self, message: str, err: Exception, **kwargs) -> None:
        """
        Log a message with severity level ERROR.
        """
        kwargs["err"] = traceback.format_exception(err)
        self._error_counter.increment()
        self._log("ERROR", 4, message, **kwargs)

    def critical(self, message: str, err: Exception, **kwargs) -> None:
        """
        Log a message with severity level CRITICAL.
        """
        kwargs["err"] = traceback.format_exception(err)
        self._error_counter.increment()
        self._log("CRITICAL", 5, message, **kwargs)

    def get_error_count(self) -> int:
        return self._error_counter.get()
