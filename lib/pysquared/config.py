"""
Class for encapsulating config.json. The goal is to
distribute these values across the files & variables
that use them. Instantiation happens in main.

Also it allow values to be set temporarily using setter
function, and values can be set permanently using the
saver functions. Following the FPrime model.
"""

import json


class RadioConfig:
    def __init__(self, config_dict: dict) -> None:
        self.sender_id: int = config_dict["sender_id"]
        self.receiver_id: int = config_dict["receiver_id"]
        self.transmit_frequency: float = config_dict["transmit_frequency"]
        self.LoRa_spreading_factor: int = config_dict["LoRa_spreading_factor"]
        self.transmit_bandwidth: int = config_dict["transmit_bandwidth"]
        self.LoRa_coding_rate: int = config_dict["LoRa_coding_rate"]
        self.transmit_power: int = config_dict["transmit_power"]
        self.start_time: int = config_dict["start_time"]


class Config:
    """
    Constructor
    """

    def __init__(self, config_path: str) -> None:
        # parses json & assigns data to variables
        with open(config_path, "r") as f:
            json_data = json.loads(f.read())

        self.radio_cfg: RadioConfig = RadioConfig(json_data)
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
        self.NORMAL_TEMP: int = json_data["NORMAL_TEMP"]
        self.NORMAL_BATT_TEMP: int = json_data["NORMAL_BATT_TEMP"]
        self.NORMAL_MICRO_TEMP: int = json_data["NORMAL_MICRO_TEMP"]
        self.NORMAL_CHARGE_CURRENT: float = json_data["NORMAL_CHARGE_CURRENT"]
        self.NORMAL_BATTERY_VOLTAGE: float = json_data["NORMAL_BATTERY_VOLTAGE"]
        self.CRITICAL_BATTERY_VOLTAGE: float = json_data["CRITICAL_BATTERY_VOLTAGE"]
        self.vlowbatt: float = json_data["vlowbatt"]
        self.battery_voltage: float = json_data["battery_voltage"]
        self.current_draw: float = json_data["current_draw"]
        self.REBOOT_TIME: int = json_data["REBOOT_TIME"]
        self.turbo_clock: bool = json_data["turbo_clock"]
        self.super_secret_code: str = json_data["super_secret_code"]
        self.repeat_code: str = json_data["repeat_code"]
        self.joke_reply: list[str] = json_data["joke_reply"]

    """
    Categorized setter functions
    """

    def set_str(self, key: str, value: str) -> None:
        """Sets the string value in the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key] = value

    def set_int(self, key: str, value: int) -> None:
        """Sets the string value in the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key] = value

    def set_float(self, key: str, value: float) -> None:
        """Sets the string value in the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key] = value

    def set_bool(self, key: str, value: bool) -> None:
        """Sets the string value in the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key] = value

    def set_list(self, key: str, value: str) -> None:
        """Adds the string value to the list specified by the key inside of the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key].append(value)

    def set_dict(self, config_key: str, dict_key: str, dict_value: float) -> None:
        """Sets the float value to the dictionary inside of the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[config_key][dict_key] = dict_value

    """
    Categorized saver functions
    """

    def save_str(self, key: str, str_value: str) -> None:
        """Saves the string value to config.json
        Saves value to disk, will persist through reboots
        """
        # add logic to write back to config
        pass

    def save_int(self, key: str, int_value: int) -> None:
        """Saves the int value to config.json
        Saves value to disk, will persist through reboots
        """
        # add logic to write back to config
        pass

    def save_float(self, key: str, float_value: float) -> None:
        """Saves the float value to config.json
        Saves value to disk, will persist through reboots
        """
        # add logic to write back to config
        pass

    def save_bool(self, key: str, bool_value: bool) -> None:
        """Saves the bool value to config.json
        Saves value to disk, will persist through reboots
        """
        # add logic to write back to config
        pass

    def save_list(self, key: str, list_value: str) -> None:
        """Saves the list value to the list in config.json
        Saves value to disk, will persist through reboots
        """
        # add logic to write back to config
        pass

    def save_dict(self, config_key: str, dict_key: str, dict_value: float) -> None:
        """Saves the float value to the dict in config.json
        Saves value to disk, will persist through reboots
        """
        # add logic to write back to config
        pass
