# This is where the magic happens!
# This file is executed on every boot (including wake-boot from deepsleep)
# Created By: Michael Pham

"""
Built for the PySquared FC Board
Version: 2.0.0
Published: Nov 19, 2024
"""

import time

import microcontroller

import lib.pysquared.pysquared as pysquared
from lib.pysquared.logger import Logger

logger = Logger()
filename = "main.py"

logger.info(
    filename=filename, software_version="2.0.0", published_date="November 19, 2024"
)

from lib.pysquared.config import Config
from lib.pysquared.pysquared import Satellite


loiter_time = 5

try:
    for i in range(loiter_time):
        # print(f"Code Starting in {loiter_time-i} seconds")
        logger.info(
            filename=filename, message=f"Code Starting in {loiter_time-i} seconds"
        )
        time.sleep(1)

    logger.debug(filename=filename, message="Initializing Config")
    config = Config()
    # print("Initializing Cubesat")
    logger.info(filename=filename, message="Initializing CubeSat")
    c = pysquared.Satellite(config, logger)
    c.watchdog_pet()

    import gc  # Garbage collection
    import traceback

    import lib.pysquared.functions as functions
    from lib.pysquared.debugcolor import co

    def debug_print(statement):
        if c.debug:
            print(co(str(c.uptime) + "[MAIN]" + str(statement), "blue", "bold"))

    f = functions.functions(c, logger=logger, config)

    def initial_boot():
        c.watchdog_pet()
        f.beacon()
        c.watchdog_pet()
        f.listen()
        c.watchdog_pet()
        # f.state_of_health()
        # f.listen()
        # c.watchdog_pet()

    try:
        c.c_boot += 1  # Increment boot number
        logger.info(filename=filename, message="Boot number: %s" % str(c.c_boot))
        logger.info(filename=filename, message=str(gc.mem_free()) + " Bytes remaining")

        initial_boot()

    except Exception as e:
        logger.error(
            filename=filename,
            message="Error in Boot Sequence: " + "".join(traceback.format_exception(e)),
        )
        # debug_print("Error in Boot Sequence: " + "".join(traceback.format_exception(e)))
    finally:
        # logger.debug("MAIN", "Something went wrong!", foo="bar")
        # NOTE: @blakejameson: the comment above shouldnt be in the finally block
        pass

    def send_imu():
        # debug_print("Looking to get imu data...")
        logger.info(filename=filename, message="Looking to get imu data...")
        IMUData = []
        c.watchdog_pet(filename=filename, message="IMU has baton")
        logger.info()
        # debug_print("IMU has baton")
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
        # debug_print("Critical in Main Loop: " + "".join(traceback.format_exception(e)))
        logger.error(
            filename=filename,
            message="Critical in Main Loop: " + "".join(traceback.format_exception(e)),
        )
        time.sleep(10)
        microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
        microcontroller.reset()
    finally:
        # debug_print("Going Neutral!")
        logger.info("Going Neutral!")

        c.RGB = (0, 0, 0)
        c.hardware["WDT"] = False

except Exception as e:
    # print(e)
    logger.error(filename=filename, message=e)
