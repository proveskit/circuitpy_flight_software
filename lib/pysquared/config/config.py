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

        self.CONFIG_SCHEMA = {
            "cubesat_name": {"type": str, "min_length": 1, "max_length": 10},
            "callsign": {"type": str, "min_length": 3, "max_length": 7},
            "super_secret_code": {"type": str, "min_length": -1, "max_length": 1},
            "repeat_code": {"type": str, "min_length": -1, "max_length": 1},
            "last_battery_temp": {"type": float, "min": -1, "max": 1},
            "normal_charge_current": {"type": float, "min": -1, "max": 1},
            "normal_battery_voltage": {"type": float, "min": -1, "max": 1},
            "critical_battery_voltage": {"type": float, "min": -1, "max": 1},
            "battery_voltage": {"type": float, "min": 5.4, "max": 8.2},
            "current_draw": {"type": float, "min": -1, "max": 1},
            "sleep_duration": {"type": int, "min": -1, "max": 1},
            "normal_temp": {"type": int, "min": 5, "max": 40},
            "normal_battery_temp": {"type": int, "min": -1, "max": 1},
            "normal_micro_temp": {"type": int, "min": -1, "max": 1},
            "reboot_time": {"type": int, "min": 3600, "max": 604800},
            "detumble_enable_z": {"type": bool, "min": False, "max": True},
            "detumble_enable_x": {"type": bool, "min": False, "max": True},
            "detumble_enable_y": {"type": bool, "min": False, "max": True},
            "debug": {"type": bool, "min": False, "max": True},
            "legacy": {"type": bool, "min": False, "max": True},
            "heating": {"type": bool, "min": False, "max": True},
            "orpheus": {"type": bool, "min": False, "max": True},
            "is_licensed": {"type": bool, "min": False, "max": True},
            "turbo_clock": {"type": bool, "min": False, "max": True},
        }

        self.RADIO_SCHEMA = {
            "receiver_id": {"type": int, "min": 0, "max": 255},
            "sender_id": {"type": int, "min": -1, "max": 1},
            "start_time": {"type": int, "min": -1, "max": 1},
            "transmit_frequency": {"type": float, "min": -1, "max": 1},
        }

        self.FSK_SCHEMA = {
            "ack_delay": {"type": float, "min": -1, "max": 1},
            "coding_rate": {"type": int, "min": 4, "max": 8},
            "cyclic_redundancy_check": {"type": bool, "min": False, "max": True},
            "max_output": {"type": bool, "min": False, "max": True},
            "spreading_factor": {"type": int, "min": 6, "max": 12},
            "transmit_power": {"type": int, "min": 5, "max": 23},
        }

        self.LORA_SCHEMA = {
            "broadcast_address": {"type": int, "min": -1, "max": 1},
            "node_address": {"type": int, "min": -1, "max": 1},
            "modulation_type": {"type": int, "min": -1, "max": 1},
        }

    # validates values from input
    def validate(self, key: str, value) -> bool:
        # first checks if key is actually part of config/radio dict
        if key in self.CONFIG_SCHEMA:
            schema = self.CONFIG_SCHEMA[key]

        elif key in self.RADIO_SCHEMA:
            schema = self.RADIO_SCHEMA[key]

        elif key in self.FSK_SCHEMA:
            schema = self.FSK_SCHEMA[key]

        elif key in self.LORA_SCHEMA:
            schema = self.LORA_SCHEMA[key]

        else:
            return False

        expected_type = schema["type"]

        # checks value is of same type
        if not isinstance(value, expected_type):
            return False

        # checks int and float range
        if isinstance(value, (int, float)):
            if "min" in schema and value < schema["min"]:
                return False
            if "max" in schema and value > schema["max"]:
                return False

        # checks string range
        if isinstance(value, str):
            if "min_length" in schema and len(value) < schema["min_lenght"]:
                return False
            if "max_length" in schema and len(value) < schema["max_length"]:
                return False

        # checks a bool value is either True or False
        if isinstance(value, bool):
            if value:
                pass
            elif not value:
                pass
            else:
                return False

        return True

    # permanently updates values
    def save_config(self, key: str, value) -> None:
        with open("config.json", "r") as f:
            json_data = json.loads(f.read())

        json_data[key] = value

        with open("config.json", "w") as f:
            f.write(json.dumps(json_data))

    # handles temp or permanent updates
    def update_config(self, key: str, value, temporary: bool) -> bool:
        # validates key and value
        if self.validate(key, value):
            if key in self.CONFIG_SCHEMA:
                # if permanent, saves to config
                if not temporary:
                    self.save_config(key, value)

                # updates RAM
                setattr(self, key, value)

            elif key in self.RADIO_SCHEMA:
                # if permanent, saves to config
                if not temporary:
                    with open("config.json", "r") as f:
                        json_data = json.loads(f.read())
                    json_data["radio"][key] = value
                    with open("config.json", "w") as f:
                        f.write(json.dumps(json_data))

                # updates RAM
                self.radio["key"] = value

            elif key in self.FSK_SCHEMA:
                # if permanent, saves to config
                if not temporary:
                    with open("config.json", "r") as f:
                        json_data = json.loads(f.read())
                    json_data["radio"]["fsk"][key] = value
                    with open("config.json", "w") as f:
                        f.write(json.dumps(json_data))

                # updates RAM
                self.radio["fsk"][key] = value

            else:
                # key is in self.LORA_SCHEMA
                # if permanent, saves to config
                if not temporary:
                    with open("config.json", "r") as f:
                        json_data = json.loads(f.read())
                    json_data["radio"]["lora"][key] = value
                    with open("config.json", "w") as f:
                        f.write(json.dumps(json_data))

                # updates RAM
                self.radio["lora"][key] = value
        else:
            return False
