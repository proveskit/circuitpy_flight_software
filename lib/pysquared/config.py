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

    def getStr(self, key: str) -> str:
        """Gets a string value from the config dictionary"""
        return self._config[key]

    def getInt(self, key: str) -> int:
        """Gets an int value from the config dictionary"""
        return self._config[key]

    def getFloat(self, key: str) -> float:
        """Gets a float value from the config dictionary"""
        return self._config[key]

    def getBool(self, key: str) -> bool:
        """Gets a bool value from the config dictionary"""
        return self._config[key]

    def getList(self, key: str) -> list[str]:
        """Gets a list value from the config dictionary"""
        return self._config[key]

    """
    Categorized setter functions
    """
    # handle errors that might occur:
    # value is not found, value type is incorrect

    def setStr(self, key: str, value: str) -> None:
        """Sets the string value in the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key] = value

    def setInt(self, key: str, value: int) -> None:
        """Sets the string value in the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key] = value

    def setFloat(self, key: str, value: float) -> None:
        """Sets the string value in the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key] = value

    def setBool(self, key: str, value: bool) -> None:
        """Sets the string value in the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key] = value

    def setList(self, key: str, value: str) -> None:
        """Sets the string value from a list inside of the config dictionary
        Does not save value to disk, will not persist through reboots
        """
        self._config[key].append(value)

    """
    Categorized saver functions
    """

    def saveStr(self, key: str, value: str) -> None:
        """Saves the string value to config.json
        Saves value to disk, will persist through reboots
        """
        self.setStr(key, value)
        self.saveToConfig()

    def saveInt(self, key: str, value: int) -> None:
        """Saves the int value to config.json
        Saves value to disk, will persist through reboots
        """
        self.setInt(key, value)
        self.saveToConfig()

    def saveFloat(self, key: str, value: float) -> None:
        """Saves the float value to config.json
        Saves value to disk, will persist through reboots
        """
        self.setFloat(key, value)
        self.saveToConfig()

    def saveBool(self, key: str, value: bool) -> None:
        """Saves the bool value to config.json
        Saves value to disk, will persist through reboots
        """
        self.setBool(key, value)
        self.saveToConfig()

    def saveList(self, key: str, value: str) -> None:
        """Saves the bool value to config.json
        Saves value to disk, will persist through reboots
        """
        self.setList(key, value)
        self.saveToConfig()

    def saveToConfig(self) -> None:
        # writes data to the json file
        with open("config.json", "w") as f:
            json.dump(self._config, f, indent=4)
