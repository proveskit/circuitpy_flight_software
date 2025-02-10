"""
Class for encapsulating config.json. The goal is to
distribute these values across the files & variables
that use them. Instantiation happens in main.

Also it allow values to be set temporarily or permanently using the
Attempting to follow the FPrime model.
"""

import json


class RadioConfig:
    def __init__(self, radio_dict: dict) -> None:
        self.sender_id: int = radio_dict["sender_id"]
        self.receiver_id: int = radio_dict["receiver_id"]
        self.transmit_frequency: float = radio_dict["transmit_frequency"]
        self.lora_spreading_factor: int = radio_dict["lora_spreading_factor"]
        self.transmit_bandwidth: int = radio_dict["transmit_bandwidth"]
        self.lora_coding_rate: int = radio_dict["lora_coding_rate"]
        self.transmit_power: int = radio_dict["transmit_power"]
        self.start_time: int = radio_dict["start_time"]


class Config:
    def __init__(self, config_path: str) -> None:
        # parses json & assigns data to variables
        with open(config_path, "r") as f:
            json_data = json.loads(f.read())

        self.radio_cfg: RadioConfig = RadioConfig(json_data["radio_cfg"])
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
