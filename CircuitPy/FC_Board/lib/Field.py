"""
This class handles communications

Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

import time
from debugcolor import co
import traceback


class Field:

    def debug_print(self, statement):
        if self.debug:
            print(co("[Field]" + statement, "pink", "bold"))

    def __init__(self, cubesat, debug):
        self.debug = debug
        self.cubesat = cubesat
        try:
            if self.cubesat.legacy:
                self.cubesat.enable_rf.value = True

            self.cubesat.radio1.spreading_factor = 8
            self.cubesat.radio1.low_datarate_optimize = False
            self.cubesat.radio1.node = 0xFB
            self.cubesat.radio1.destination = 0xFA
            self.cubesat.radio1.receive_timeout = 10
            self.cubesat.radio1.enable_crc = True
            if self.cubesat.radio1.spreading_factor > 8:
                self.cubesat.radio1.low_datarate_optimize = True
        except Exception as e:
            self.debug_print(
                "Error Defining Radio features: "
                + "".join(traceback.format_exception(e))
            )

    def Beacon(self, msg):
        try:
            if self.cubesat.is_licensed:
                self.debug_print("I am beaconing: " + str(msg))
                self.cubesat.radio1.send(msg)
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
