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
    _config: dict

    def __init__(self) -> None:
        # parses json & assigns data to variables
        with open("config.json", "r") as f:
            json_data = f.read()
        self._config = json.loads(json_data)

    """
    Categorized getter functions
    """

    def getStrValue(self, strVariable: str) -> str:
        return self._config[strVariable]

    def getIntValue(self, intVariable: str) -> int:
        return self._config[intVariable]

    def getFloatValue(self, floatVariable: str) -> float:
        return self._config[floatVariable]

    def getBoolValue(self, boolVariable: str) -> bool:
        return self._config[boolVariable]

    def getListValue(self, listVariable: str) -> list[str]:
        return self._config[listVariable]

    def getCommands(self) -> dict:
        return commandsConfig.commands

    """
    Categorized setter functions
    """

    def setStrValue(self, key: str, strValue: str) -> None:
        self._config[key] = strValue

    def setIntValue(self, key: str, intValue: int) -> None:
        self._config[key] = intValue

    def setFloatValue(self, key: str, floatValue: float) -> None:
        self._config[key] = floatValue

    def setBoolValue(self, key: str, boolValue: bool) -> None:
        self._config[key] = boolValue

    def setListValue(
        self, key: str, listValue: str
    ) -> None:  # check this one might not even be a good idea to set anyway
        self._config[key] = listValue


print("Initializing Config")
config = Config()
