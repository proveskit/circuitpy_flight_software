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

import digitalio
import microcontroller

try:
    from board_definitions import proveskit_rp2040_v4 as board
except ImportError:
    import board

import lib.pysquared.functions as functions
import lib.pysquared.nvm.register as register
import lib.pysquared.pysquared as pysquared
from lib.pysquared.config.config import Config
from lib.pysquared.hardware.digitalio import initialize_pin
from lib.pysquared.hardware.rfm9x.factory import RFM9xFactory
from lib.pysquared.hardware.rfm9x.manager import RFM9xManager
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.counter import Counter
from lib.pysquared.nvm.flag import Flag
from lib.pysquared.rtc.rtc_common import RTC
from lib.pysquared.sleep_helper import SleepHelper
from version import __version__

RTC.init()

logger: Logger = Logger(
    error_counter=Counter(index=register.ERRORCNT, datastore=microcontroller.nvm),
    colorized=False,
)

logger.info("Booting", software_version=__version__, published_date="November 19, 2024")

loiter_time: int = 5

try:
    for i in range(loiter_time):
        logger.info(f"Code Starting in {loiter_time-i} seconds")
        time.sleep(1)

    logger.debug("Initializing Config")
    config: Config = Config("config.json")

    c = pysquared.Satellite(config, logger, __version__)
    c.watchdog_pet()
    sleep_helper = SleepHelper(c, logger)

    radio_manager = RFM9xManager(
        logger,
        Flag(index=register.FLAG, bit_index=7, datastore=microcontroller.nvm),
        RFM9xFactory(
            c.spi0,
            initialize_pin(logger, board.SPI0_CS0, digitalio.Direction.OUTPUT, True),
            initialize_pin(logger, board.RF1_RST, digitalio.Direction.OUTPUT, True),
            config.radio,
        ),
        config.is_licensed,
    )

    f = functions.functions(c, logger, config, sleep_helper, radio_manager)

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
        logger.error("Error in Boot Sequence", e)

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

        sleep_helper.long_hibernate()

    def minimum_power_operations():
        initial_boot()
        c.watchdog_pet()

        sleep_helper.short_hibernate()

    ######################### MAIN LOOP ##############################
    try:
        while True:
            # L0 automatic tasks no matter the battery level
            c.check_reboot()

            if c.power_mode == "critical":
                c.rgb = (0, 0, 0)
                critical_power_operations()

            elif c.power_mode == "minimum":
                c.rgb = (255, 0, 0)
                minimum_power_operations()

            elif c.power_mode == "normal":
                c.rgb = (255, 255, 0)
                main()

            elif c.power_mode == "maximum":
                c.rgb = (0, 255, 0)
                main()

            else:
                f.listen()

    except Exception as e:
        logger.critical("Critical in Main Loop", e)
        time.sleep(10)
        microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
        microcontroller.reset()
    finally:
        logger.info("Going Neutral!")

        c.rgb = (0, 0, 0)
        c.hardware["WDT"] = False

except Exception as e:
    logger.critical("An exception occured within main.py", e)
