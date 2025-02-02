"""
This class handles communications

Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

from lib.pysquared.logger import Logger


class Field:
    def __init__(self, cubesat, logger: Logger):
        self.cubesat = cubesat
        self.logger = logger

    def Beacon(self, msg):
        try:
            if self.cubesat.is_licensed:
                self.logger.info(
                    "I am beaconing",
                    beacon=str(msg),
                    success=str(self.cubesat.radio1.send(bytes(msg, "UTF-8"))),
                )
            else:
                self.logger.debug(
                    "Please toggle licensed variable in code once you obtain an amateur radio license",
                )
        except Exception as e:
            self.logger.error("There was an error while Beaconing", err=e)

    def troubleshooting(self):
        # this is for troubleshooting comms
        pass

    def __del__(self):
        self.logger.debug("Object Destroyed!")
