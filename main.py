# This is where the magic happens!
# This file is executed on every boot (including wake-boot from deepsleep)
# Created By: Michael Pham

"""
Built for the PySquared FC Board
Version: 2.0.0
Published: Nov 19, 2024
"""

import gc
import time

import microcontroller

import lib.pysquared.functions as functions
import lib.pysquared.nvm.register as register
import lib.pysquared.pysquared as pysquared
from lib.adafruit_rfm.rfm_common import RFMSPI
from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.counter import Counter
from lib.pysquared.nvm.flag import Flag
from lib.pysquared.radio import Radio

logger: Logger = Logger(
    error_counter=Counter(index=register.ERRORCNT, datastore=microcontroller.nvm)
)
logger.info("Booting", software_version="2.0.0", published_date="November 19, 2024")


loiter_time: int = 5

try:
    for i in range(loiter_time):
        logger.info(f"Code Starting in {loiter_time-i} seconds")
        time.sleep(1)

    logger.debug("Initializing Config")
    config: Config = Config()

    c = pysquared.Satellite(logger, config)
    c.watchdog_pet()

    radio: RFMSPI = Radio.create(
        Flag(
            index=register.NVM.FLAG,
            bit_index=register.FLAG_01.USE_FSK,
            datastore=microcontroller.nvm,
        ),
        logger,
        c.spi0,
        config.get_dict("radio_cfg")["sender_id"],
        config.get_dict("radio_cfg")["receiver_id"],
        config.get_dict("radio_cfg")["transmit_frequency"],
        config.get_dict("radio_cfg")["transmit_power"],
        config.get_dict("radio_cfg")["lora_spreading_factor"],
    )

    f = functions.functions(logger, config, c, radio)

    def initial_boot():
        c.watchdog_pet()
        f.beacon()
        c.watchdog_pet()
        f.listen()
        c.watchdog_pet()

    try:
        c.boot_count.increment()

        logger.info(
            "FC Board Stats",
            bytes_remaining=gc.mem_free(),
            boot_number=c.boot_count.get(),
        )

        initial_boot()

    except Exception as e:
        logger.error("Error in Boot Sequence", err=e)

    finally:
        pass

    def send_imu_data():
        logger.info("Looking to get imu data...")
        IMUData = []
        c.watchdog_pet()
        logger.info("IMU has baton")
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

        send_imu_data()

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
        logger.critical("Critical in Main Loop", err=e)
        time.sleep(10)
        microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
        microcontroller.reset()
    finally:
        logger.info("Going Neutral!")

        c.RGB = (0, 0, 0)
        c.hardware["WDT"] = False

except Exception as e:
    logger.error("An exception occured within main.py", err=e)
