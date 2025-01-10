import adafruit_logging as logging
import json
import time


class Logger:

    def __init__(self):
        self.internal_logger = logging.getLogger("logger")
        self.internal_logger.setLevel(logging.DEBUG)
        print_handler = logging.StreamHandler()
        self.internal_logger.addHandler(print_handler)
        default_formatter = logging.Formatter()

        print_handler.setFormatter(default_formatter)
        self.internal_logger.info("Default formatter example")

        timestamp_formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s: %(message)s"
        )
        print_handler.setFormatter(timestamp_formatter)
        self.internal_logger.info("Timestamp formatter example")

        custom_vals_formatter = logging.Formatter(
            fmt="%(ip)s %(levelname)s: %(message)s", defaults={"ip": "192.168.1.188"}
        )
        print_handler.setFormatter(custom_vals_formatter)
        self.internal_logger.info("Custom formatter example")

        bracket_timestamp_formatter = logging.Formatter(
            fmt="{asctime} {levelname}: {message}", style="{"
        )
        print_handler.setFormatter(bracket_timestamp_formatter)
        self.internal_logger.info("Timestamp formatter bracket style example")

    def debug(self, filename, message, **kwargs):
        # logging.basicConfig(level=logging.INFO, format='%(message)s')
        full_message = "[" + filename + "]" + message
        now = time.localtime()
        asctime = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        kwargs["time"] = asctime
        output = "[%s] %s >>> %s" % (filename, message, json.dumps(kwargs))
        kwargs["message"] = message
        kwargs["level"] = "DEBUG"
        alternate_output = "[%s] >>> %s" % (filename, json.dumps(kwargs))
        ideal_output = json.dumps(kwargs)
        print(kwargs)
        print(output)
        print(alternate_output)
        print(ideal_output)
        self.internal_logger.debug(output)
        self.internal_logger.debug(alternate_output)

    def info(self, message, *args):
        self.internal_logger.info(message, *args)

    def warning(self, message, *args):
        self.internal_logger.warning(message, *args)

    def error(self, message, *args):
        self.internal_logger.error(message, *args)

    def critical(self, message, *args):
        self.internal_logger.critical(message, *args)
