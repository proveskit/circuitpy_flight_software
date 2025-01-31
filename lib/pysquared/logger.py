import json
import time


class Logger:
    def __init__(self, log_to_stdout=True, log_file=None) -> None:
        self.logToStandardOut = log_to_stdout
        self.log_file = log_file  # File object to write logs to

    def _log(self, level: str, message: str, **kwargs) -> None:
        """
        Log a message with a given severity level and any additional key/values.
        """
        log_entry = {
            "level": level,
            "msg": message,
        }

        # Manually format the time since time.strftime is not available in CircuitPython
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        log_entry["time"] = asctime

        log_entry.update(kwargs)
        json_output = json.dumps(log_entry)
        if self.logToStandardOut:
            print(json_output)
        if self.log_file:
            self.log_file.write(json_output + "\n")
            self.log_file.flush()

    def debug(self, message: str, **kwargs) -> None:
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        self._log("CRITICAL", message, **kwargs)
