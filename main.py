# This is where the magic happens!
# This file is executed on every boot (including wake-boot from deepsleep)
# Created By: Michael Pham

"""
Built for the PySquared FC Board
Version: 2.0.0
Published: Nov 19, 2024
"""

import asyncio
import time

import microcontroller

import lib.pysquared.nvm.register as register
import lib.pysquared.pysquared as pysquared
from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.counter import Counter

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

    c = pysquared.Satellite(config, logger)
    c.watchdog_pet()

    import gc  # Garbage collection

    import lib.pysquared.functions as functions

    f = functions.functions(c, logger, config)

    async def initial_boot(c, f):
        await f.beacon()
        await f.listen()

    async def send_imu_data(c, f):
        logger.info("Looking to get imu data...")
        IMUData = []
        logger.info("IMU has baton")
        IMUData = await f.get_imu_data()
        await f.send(IMUData)

    async def main_loop(c, f):
        await f.beacon()
        await f.listen_loiter()
        await f.state_of_health()
        await f.listen_loiter()
        await f.all_face_data()
        await f.send_face()
        await f.listen_loiter()
        await send_imu_data(c, f)
        await f.listen_loiter()
        await f.joke()
        await f.listen_loiter()

    async def critical_power_operations(c, f):
        await initial_boot(c, f)
        await f.Long_Hybernate()

    async def minimum_power_operations(c, f):
        await initial_boot(c, f)
        await f.Short_Hybernate()

    async def main():
        try:
            c.boot_count.increment()

            logger.info(
                "FC Board Stats",
                bytes_remaining=gc.mem_free(),
                boot_number=c.boot_count.get(),
            )

            await initial_boot(c, f)

            # Main operation loop with watchdog running in background
            async with c.start_watchdog():
                while True:
                    c.check_reboot()

                    if c.power_mode == "critical":
                        c.RGB = (0, 0, 0)
                        await critical_power_operations(c, f)
                    elif c.power_mode == "minimum":
                        c.RGB = (255, 0, 0)
                        await minimum_power_operations(c, f)
                    elif c.power_mode == "normal":
                        c.RGB = (255, 255, 0)
                        await main_loop(c, f)
                    elif c.power_mode == "maximum":
                        c.RGB = (0, 255, 0)
                        await main_loop(c, f)
                    else:
                        await f.listen()

        except Exception as e:
            logger.critical("Critical in Main Loop", err=e)
            await asyncio.sleep(10)
            microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
            microcontroller.reset()
        finally:
            logger.info("Going Neutral!")

            c.RGB = (0, 0, 0)
            c.hardware["WDT"] = False

    # Run the async main function
    asyncio.run(main())

except Exception as e:
    logger.error("An exception occured within main.py", err=e)
