"""
This class handles communications

Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

import traceback

from lib.pysquared.debugcolor import co
from lib.pysquared.logger import Logger


class Field:
    def debug_print(self, statement):
        if self.debug:
            print(co("[Field]" + statement, "pink", "bold"))

    def __init__(self, cubesat, debug, logger: Logger):
        self.debug = debug
        self.cubesat = cubesat
        self.logger = logger

    def Beacon(self, msg):
        try:
            if self.cubesat.is_licensed:
                self.logger.info(message="I am beaconing: " + str(msg))
                self.logger.info(
                    message="Message Success: "
                    + str(self.cubesat.radio1.send(bytes(msg, "UTF-8"))),
                )
            else:
                self.logger.debug(
                    message="Please toggle licensed variable in code once you obtain an amateur radio license",
                )
        except Exception as e:
            self.logger.error(
                message="Tried Beaconing but encountered error: ".join(
                    traceback.format_exception(e)
                ),
            )

    def troubleshooting(self):
        # this is for troubleshooting comms
        pass

    def __del__(self):
        self.logger.debug(message="Object Destroyed!")
