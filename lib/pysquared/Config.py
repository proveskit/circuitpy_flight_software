"""
Class for encapsulating config.json. The goal is to
distribute these values across the files & variables
that use them. Instantiation happens in main.

Also it allow values to be set temporarily using setter
function, and values can be set permanently using the
saver functions. Following the FPrime model.
"""

import json

import lib.pysquared.commandsConfig as commandsConfig


class Config:
    """
    Constructor
    """

    def __init__(self) -> None:
        # parses json & assigns data to variables
        with open("config.json", "r") as f:
            json_data = f.read()
        self._config: dict = json.loads(json_data)

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

    """
    Categorized saver functions
    """


#    def saveStrValue(self, key: str, strValue: str) -> None:
# add logic to write back to config

#    def saveIntValue(self, key: str, intValue: int) -> None:
# add logic to write back to config

#    def saveFloatValue(self, key: str, floatValue: float) -> None:
# add logic to write back to config

#    def saveBoolValue(self, key: str, boolValue: bool) -> None:
# add logic to write back to config
