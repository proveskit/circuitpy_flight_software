"""
Class for encapsulating config.json. The goal is to
distribute these values across the files & variables
that use them when instantiated.

Also it allow values to be set temporarily before being
made permanent on restart. Following the FPrime model
"""

import json
import commandsConfig


class Config:
    def __init__(self) -> None:
        # parses json & assigns data to variables
        with open("config.json", "r") as f:
            json_data = f.read()
        config = json.loads(json_data)

        """
        function.py initializations
        """
        self.functions_cubesatName: str = config["cubesatName"]
        self.functions_jokes: list[str] = config["jokes"]
        self.functions_last_battery_temp: float = config["last_battery_temp"]
        self.functions_sleep_duration: int = config["sleep_duration"]
        self.functions_callsign: str = config["callsign"]

        """
        pysquared.py initializations
        """
        self.pysquared_debug: bool = config["debug"]
        self.pysquared_legacy: bool = config[
            "legacy"
        ]  # Define if the board is used with legacy or not
        self.pysquared_heating: bool = config["heating"]  # Currently not used
        self.pysquared_orpheus: bool = config[
            "orpheus"
        ]  # Define if the board is used with Orpheus or not
        self.pysquared_is_licensed: bool = config["is_licensed"]

        self.pysquared_NORMAL_TEMP: int = config["NORMAL_TEMP"]
        self.pysquared_NORMAL_BATT_TEMP: int = config[
            "NORMAL_BATT_TEMP"
        ]  # Set to 0 BEFORE FLIGHT!!!!!
        self.pysquared_NORMAL_MICRO_TEMP: int = config["NORMAL_MICRO_TEMP"]
        self.pysquared_NORMAL_CHARGE_CURRENT: float = config["NORMAL_CHARGE_CURRENT"]
        self.pysquared_NORMAL_BATTERY_VOLTAGE: float = config[
            "NORMAL_BATTERY_VOLTAGE"
        ]  # 6.9
        self.pysquared_CRITICAL_BATTERY_VOLTAGE: float = config[
            "CRITICAL_BATTERY_VOLTAGE"
        ]  # 6.6
        self.pysquared_vlowbatt: float = config["vlowbatt"]
        self.pysquared_battery_voltage: float = config[
            "battery_voltage"
        ]  # default value for testing REPLACE WITH REAL VALUE
        self.pysquared_current_draw: float = config[
            "current_draw"
        ]  # default value for testing REPLACE WITH REAL VALUE
        self.pysquared_REBOOT_TIME: int = config["REBOOT_TIME"]  # 1 hour
        self.pysquared_turbo_clock: bool = config["turbo_clock"]

        """
        cdh.py initializations
        """
        self.cdh_commands = commandsConfig.commands
        self.cdh_jokereply = config["jokereply"]
        self.cdh_super_secret_code = config["super_secret_code"].encode("utf-8")
        self.cdh_repeat_code = config["repeat_code"].encode("utf-8")
