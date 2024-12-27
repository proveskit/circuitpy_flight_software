"""
Created by Nicole Maggard and Michael Pham 8/19/2022
Updated for Yearling by Nicole Maggard and Rachel Sarmiento 2/4/2023
Updated again for Orpheus by Michael Pham 9/30/2024
This is where the processes get scheduled, and satellite operations are handeled
"""

from lib.pysquared import cubesat as c

c.watchdog_pet()

import asyncio
import time
import traceback
import gc  # Garbage collection
import microcontroller  # circuitpython module will need stub/mock for IDE intellesense, Issue #27
import lib.functions as functions
from lib.debugcolor import co

beacon_interval = 15


def debug_print(statement):
    if c.debug:
        print(co(str(c.uptime) + "[MAIN]" + str(statement), "blue", "bold"))


f = functions.functions(c)


def initial_boot():
    c.watchdog_pet()
    f.beacon()
    c.watchdog_pet()
    f.listen()
    c.watchdog_pet()
    # f.state_of_health()
    # f.listen()
    c.watchdog_pet()


try:
    c.c_boot += 1  # Increment boot number
    debug_print("Boot number: " + str(c.c_boot))
    debug_print(str(gc.mem_free()) + " Bytes remaining")

    initial_boot()

except Exception as e:
    debug_print("Error in Boot Sequence: " + "".join(traceback.format_exception(e)))
finally:
    debug_print("Something went wrong!")


def send_imu():
    debug_print("Looking to get imu data...")
    IMUData = []
    c.watchdog_pet()
    debug_print("IMU has baton")
    IMUData = f.get_imu_data()
    c.watchdog_pet()
    f.send(IMUData)


def main():
    f.beacon()

    f.listen_loiter()

    f.state_of_health()

    f.listen_loiter()

    f.all_face_data()
    c.watchdog_pet()
    f.send_face()

    f.listen_loiter()

    send_imu()

    f.listen_loiter()

    f.joke()

    f.listen_loiter()


def critical_power_operations():

    initial_boot()
    c.watchdog_pet()

    f.Long_Hybernate()


def minimum_power_operations():

    initial_boot()
    c.watchdog_pet()

    f.Short_Hybernate()


######################### MAIN LOOP ##############################
try:

    while True:
        # L0 automatic tasks no matter the battery level
        c.check_reboot()

        if c.power_mode == "critical":
            c.RGB = (0, 0, 0)
            critical_power_operations()

        elif c.power_mode == "minimum":
            c.RGB = (255, 0, 0)
            minimum_power_operations()

        elif c.power_mode == "normal":
            c.RGB = (255, 255, 0)
            main()

        elif c.power_mode == "maximum":
            c.RGB = (0, 255, 0)
            main()

        else:
            f.listen()

except Exception as e:
    debug_print("Critical in Main Loop: " + "".join(traceback.format_exception(e)))
    time.sleep(10)
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()
finally:
    debug_print("Going Neutral!")

    c.RGB = (0, 0, 0)
    c.hardware["WDT"] = False
