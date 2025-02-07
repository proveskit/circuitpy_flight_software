import gc
import time

import alarm

from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite

try:
    from typing import Literal

    import circuitpython_typing
except Exception:
    pass


class SleepHelper:
    def __init__(self, cubesat: Satellite, logger: Logger, config: Config):
        self.cubesat: Satellite = cubesat
        self.logger: Logger = logger
        self.config: Config = config

    def safe_sleep(self, duration: int = 15) -> None:
        self.logger.info("Setting Safe Sleep Mode")

        iterations: int = 0

        while duration >= 15 and iterations < 12:
            time_alarm: circuitpython_typing.Alarm = alarm.time.TimeAlarm(
                monotonic_time=time.monotonic() + 15
            )

            alarm.light_sleep_until_alarms(time_alarm)
            duration -= 15
            iterations += 1

            self.cubesat.watchdog_pet()

    def short_hibernate(self) -> Literal[True]:
        self.logger.debug("Short Hibernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot.toggle(True)
        self.cubesat.watchdog_pet()
        self.safe_sleep(120)

        self.cubesat.enable_rf.value = True
        return True

    def long_hibernate(self) -> Literal[True]:
        self.logger.debug("LONG Hibernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot.toggle(True)
        self.cubesat.watchdog_pet()
        self.safe_sleep(600)

        self.cubesat.enable_rf.value = True
        return True
