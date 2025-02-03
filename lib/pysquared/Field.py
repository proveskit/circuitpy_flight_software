"""
This class handles communications

Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

from lib.adafruit_rfm.rfm_common import RFMSPI
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite


class Field:
    def __init__(self, logger: Logger, cubesat: Satellite, radio: RFMSPI):
        self._cubesat: Satellite = cubesat
        self._log: Logger = logger
        self._radio: RFMSPI = radio

    def Beacon(self, msg):
        try:
            if self._cubesat.is_licensed:
                self._log.info(
                    "I am beaconing",
                    beacon=str(msg),
                    success=str(self._radio.send(bytes(msg, "UTF-8"))),
                )
            else:
                self._log.debug(
                    "Please toggle licensed variable in code once you obtain an amateur radio license",
                )
        except Exception as e:
            self._log.error("There was an error while Beaconing", err=e)

    def troubleshooting(self):
        # this is for troubleshooting comms
        pass

    def __del__(self):
        self._log.debug("Object Destroyed!")
