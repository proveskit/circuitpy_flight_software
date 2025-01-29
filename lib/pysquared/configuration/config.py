"""
Class for encapsulating config.json. The goal is to
distribute these values across the files & variables
that use them. Instantiation happens in main.

Also it allow values to be set temporarily using setter
functions, and values can be set permanently using the
saver functions. Following the FPrime model.
"""

import json

from lib.pysquared.logger import Logger


class Config:
    """
    Constructor
    """

    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        # parses json & assigns data to variables
        try:
            with open("config.json", "r") as f:
                json_data = f.read()
            self._config: dict = json.loads(json_data)
            self._logger.info("JSON Parsing Successful")
        except Exception:
            self._logger.error("JSON Parsing Unsuccessful")

        # exception notes
        # emit a value type and error from the getter functions
        # if we want to implement exception handling

    """
    Categorized getter functions
    """
    # handle errors that might occur:
    # value is not found, value type is incorrect

    def get_str(self, key: str) -> str:
        """Gets a string value from the config dictionary"""
        return self._config[key]

    def get_int(self, key: str) -> int:
        """Gets an int value from the config dictionary"""
        return self._config[key]

    def get_float(self, key: str) -> float:
        """Gets a float value from the config dictionary"""
        return self._config[key]

    def get_bool(self, key: str) -> bool:
        """Gets a bool value from the config dictionary"""
        return self._config[key]

    def get_list(self, key: str) -> list[str]:
        """Gets a list value from the config dictionary"""
        return self._config[key]

    def get_dict(self, key: str) -> dict[str, float]:
        """Gets a dictionary value from the config dictionary"""
        return self._config[key]

    """
    Categorized setter functions
    """
    # handle errors that might occur:
    # key does not match database, value is of different type

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
    # handle errors that might occur:
    # setter functions returned error, parsing to config returned error

    def save_str(self, key: str, str_value: str) -> None:
        """Saves the string value to config.json
        Saves value to disk, will persist through reboots
        """
        self.set_str(key, str_value)
        self.save_to_config()

    def save_int(self, key: str, int_value: int) -> None:
        """Saves the int value to config.json
        Saves value to disk, will persist through reboots
        """
        self.set_int(key, int_value)
        self.save_to_config()

    def save_float(self, key: str, float_value: float) -> None:
        """Saves the float value to config.json
        Saves value to disk, will persist through reboots
        """
        self.set_float(key, float_value)
        self.save_to_config()

    def save_bool(self, key: str, bool_value: bool) -> None:
        """Saves the bool value to config.json
        Saves value to disk, will persist through reboots
        """
        self.set_bool(key, bool_value)
        self.save_to_config()

    def save_list(self, key: str, list_value: str) -> None:
        """Saves the list value to the list in config.json
        Saves value to disk, will persist through reboots
        """
        self.set_list(key, list_value)
        self.save_to_config()

    def save_dict(self, config_key: str, dict_key: str, dict_value: float) -> None:
        """Saves the float value to the dict in config.json
        Saves value to disk, will persist through reboots
        """
        self.set_list(config_key, dict_key, dict_value)
        self.save_to_config()

    """
    Parser function
    """
    # handle errors that might occur:
    # config file does not exist, parsing failed

    def save_to_config(self) -> None:
        # writes data to the json file
        with open("config.json", "w") as f:
            json.dump(self._config, f, indent=4)
