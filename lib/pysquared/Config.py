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
    function.py getter functions
    """

    def getCubesatName(self) -> str:
        return self._config["cubesatName"]

    def getJokes(self) -> list[str]:
        return self._config["jokes"]

    def getLastBatteryTemp(self) -> float:
        return self._config["last_battery_temp"]

    def getSleepDuration(self) -> int:
        return self._config["sleep_duration"]

    def getCallsign(self) -> str:
        return self._config["callsign"]

    def getDetumbleZ(self) -> bool:
        return self._config["detumble_enable_z"]

    def getDetumbleX(self) -> bool:
        return self._config["detumble_enable_x"]

    def getDetumbleY(self) -> bool:
        return self._config["detumble_enable_y"]

    """
    pysquared.py getter functions
    """

    def getDebug(self) -> bool:
        return self._config["debug"]

    def getLegacy(self) -> bool:
        return self._config["legacy"]

    def getHeating(self) -> bool:
        return self._config["heating"]

    def getOrpheus(self) -> bool:
        return self._config["orpheus"]

    def getIsLicensed(self) -> bool:
        return self._config["is_licensed"]

    def getNormalTemp(self) -> int:
        return self._config["NORMAL_TEMP"]

    def getNormalBattTemp(self) -> int:
        return self._config["NORMAL_BATT_TEMP"]

    def getNormalMicroTemp(self) -> int:
        return self._config["NORMAL_MICRO_TEMP"]

    def getNormalChargeCurrent(self) -> float:
        return self._config["NORMAL_CHARGE_CURRENT"]

    def getNormalBatteryVoltage(self) -> float:
        return self._config["NORMAL_BATTERY_VOLTAGE"]

    def getCriticalBatteryVoltage(self) -> float:
        return self._config["CRITICAL_BATTERY_VOLTAGE"]

    def getVlowbatt(self) -> float:
        return self._config["vlowbatt"]

    def getBatteryVoltage(self) -> float:
        return self._config["battery_voltage"]

    def getCurrentDraw(self) -> float:
        return self._config["current_draw"]

    def getRebootTime(self) -> int:
        return self._config["REBOOT_TIME"]

    def getTurboClock(self) -> bool:
        return self._config["turbo_clock"]

    """
    cdh.py getter functions
    """

    def getCommands(self) -> dict:
        return commandsConfig.commands

    def getJokeReply(self) -> list[str]:
        return self._config["jokereply"]

    def getSuperSecretCode(self) -> str:
        return self._config["super_secret_code"].encode("utf-8")

    def getRepeatCode(self) -> str:
        return self._config["repeat_code"].encode("utf-8")

    """
    """
    # function.py setter functions
    """
    def setCubesatName(self) -> None:

    def setJokes(self) -> None:

    def setLastBatteryTemp(self) -> None:

    def setSleepDuration(self) -> None:

    def setCallsign(self) -> None:

    def setDetumbleZ(self) -> None:

    def setDetumbleX(self) -> None:

    def setDetumbleY(self) -> None:


    """
    # pysquared.py setter functions
    """
    def setDebug(self) -> None:

    def setLegacy(self) -> None:

    def setHeating(self) -> None:

    def setOrpheus(self) -> None:

    def setIsLicensed(self) -> None:

    def setNormalTemp(self) -> None:

    def setNormalBattTemp(self) -> None:

    def setNormalMicroTemp(self) -> None:

    def setNormalChargeCurrent(self) -> None:

    def setNormalBatteryVoltage(self) -> None:

    def setCriticalBatteryVoltage(self) -> None:

    def setVlowbatt(self) -> None:

    def setBatteryVoltage(self) -> None:

    def setCurrentDraw(self) -> None:

    def setRebootTime(self) -> None:

    def setTurboClock(self) -> None:


    """
    # cdh.py setter functions
    """
    def setCommands(self) -> None:

    def setJokeReply(self) -> None:

    def setSuperSecretCode(self) -> None:

    def setRepeatCode(self) -> None:
    """
