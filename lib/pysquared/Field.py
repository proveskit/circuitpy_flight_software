"""
This class handles communications

Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

import traceback

from lib.pysquared.debugcolor import co


class Field:
    def debug_print(self, statement):
        if self.debug:
            print(co("[Field]" + statement, "pink", "bold"))

    def __init__(self, cubesat, debug):
        self.debug = debug
        self.cubesat = cubesat

    def Beacon(self, msg):
        try:
            if self.cubesat.is_licensed:
                self.debug_print("I am beaconing: " + str(msg))
                print(
                    "Message Success: "
                    + str(self.cubesat.radio1.send(bytes(msg, "UTF-8")))
                )
            else:
                self.debug_print(
                    "Please toggle licensed variable in code once you obtain an amateur radio license"
                )
        except Exception as e:
            self.debug_print(
                "Tried Beaconing but encountered error: ".join(
                    traceback.format_exception(e)
                )
            )

    def troubleshooting(self):
        # this is for troubleshooting comms
        pass

    def __del__(self):
        self.debug_print("Object Destroyed!")
