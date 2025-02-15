"""
This class handles communications

Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

from lib.pysquared.hardware.rfm9x.manager import RFM9xManager
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite

try:
    from typing import Any
except Exception:
    pass


class Field:
    def __init__(
        self, cubesat: Satellite, logger: Logger, radio_manager: RFM9xManager
    ) -> None:
        self.cubesat: Satellite = cubesat
        self.logger: Logger = logger
        self.radio_manager: RFM9xManager = radio_manager

    def Beacon(self, msg: Any):
        if not self.cubesat.is_licensed:
            self.logger.debug(
                "Please toggle licensed variable in code once you obtain an amateur radio license",
            )
            return

        try:
            sent = self.radio_manager.radio.send(bytes(msg, "UTF-8"))
        except Exception as e:
            self.logger.error("There was an error while Beaconing", e)
            return

        self.logger.info("I am beaconing", beacon=str(msg), success=str(sent))

    def troubleshooting(self) -> None:
        # this is for troubleshooting comms
        pass

    def __del__(self) -> None:
        self.logger.debug("Object Destroyed!")
