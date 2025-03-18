"""
Class for encapsulating config.json. The goal is to
distribute these values across the files & variables
that use them. Instantiation happens in main.

Also it allow values to be set temporarily or permanently using the
Attempting to follow the FPrime model.
"""

import json

from lib.pysquared.config.radio import RadioConfig


class Config:
    def __init__(self, config_path: str) -> None:
        # parses json & assigns data to variables
        with open(config_path, "r") as f:
            json_data = json.loads(f.read())

        self.radio: RadioConfig = RadioConfig(json_data["radio"])
        self.cubesat_name: str = json_data["cubesat_name"]
        self.callsign: str = json_data["callsign"]
        self.last_battery_temp: float = json_data["last_battery_temp"]
        self.sleep_duration: int = json_data["sleep_duration"]
        self.detumble_enable_z: bool = json_data["detumble_enable_z"]
        self.detumble_enable_x: bool = json_data["detumble_enable_x"]
        self.detumble_enable_y: bool = json_data["detumble_enable_y"]
        self.jokes: list[str] = json_data["jokes"]
        self.debug: bool = json_data["debug"]
        self.legacy: bool = json_data["legacy"]
        self.heating: bool = json_data["heating"]
        self.orpheus: bool = json_data["orpheus"]
        self.is_licensed: bool = json_data["is_licensed"]
        self.normal_temp: int = json_data["normal_temp"]
        self.normal_battery_temp: int = json_data["normal_battery_temp"]
        self.normal_micro_temp: int = json_data["normal_micro_temp"]
        self.normal_charge_current: float = json_data["normal_charge_current"]
        self.normal_battery_voltage: float = json_data["normal_battery_voltage"]
        self.critical_battery_voltage: float = json_data["critical_battery_voltage"]
        self.battery_voltage: float = json_data["battery_voltage"]
        self.current_draw: float = json_data["current_draw"]
        self.reboot_time: int = json_data["reboot_time"]
        self.turbo_clock: bool = json_data["turbo_clock"]
        self.super_secret_code: str = json_data["super_secret_code"]
        self.repeat_code: str = json_data["repeat_code"]
        self.joke_reply: list[str] = json_data["joke_reply"]

    # validates values from input
    def validate(self, key: str, value) -> bool:
        if hasattr(self, key):
            if isinstance(value, str):
                if self.validate_string(value):
                    return True
                return False

            elif isinstance(value, int):
                if self.validate_int(value):
                    return True
                return False

            elif isinstance(value, float):
                if self.validate_float(value):
                    return True
                return False

            elif isinstance(value, bool):
                if self.validate_bool(value):
                    return True
                return False

            elif isinstance(value, dict):
                if self.validate_dict(value):
                    return True
                return False

            return True
        else:
            print("Member variable not found")
            return False

    def validate_string(self, value: str) -> bool:
        pass

    def validate_int(self, value: int) -> bool:
        pass

    def validate_float(self, value: float) -> bool:
        pass

    def validate_bool(self, value: bool) -> bool:
        pass

    def validate_dict(self, value: dict) -> bool:
        pass

    # permanently updates values
    def save_config(self, key: str, value) -> None:
        with open("config.json", "r") as f:
            json_data = json.loads(f.read())

        json_data[key] = value

        with open("config.json", "w") as f:
            f.write(json.dumps(json_data))

    # updates config values
    def update_config(self, key: str, value, temporary: bool) -> bool:
        if self.validate(key, value):
            if not temporary:
                self.save_config(key, value)
            else:
                setattr(self, key, value)
            return True
        else:
            return False
