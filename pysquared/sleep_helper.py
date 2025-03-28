import gc
import time

import alarm

from .logger import Logger
from .satellite import Satellite

try:
    from typing import Literal

    import circuitpython_typing
except Exception:
    pass


class SleepHelper:
    """
    Class responsible for sleeping the Satellite to conserve power
    """

    def __init__(self, cubesat: Satellite, logger: Logger):
        """
        Creates a SleepHelper object.

        :param cubesat: The Satellite object
        :param logger: The Logger object allowing for log output

        """
        self.cubesat: Satellite = cubesat
        self.logger: Logger = logger

    def safe_sleep(self, duration: int = 15) -> None:
        """
        Puts the Satellite to sleep for specified duration, in seconds.

        Current implementation results in an actual sleep duration that is a multiple of 15.
        Current implementation only allows for a maximum sleep duration of 180 seconds.

        :param duration: Specified time, in seconds, to sleep the Satellite for
        """

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
        """Puts the Satellite to sleep for 120 seconds"""

        self.logger.debug("Short Hibernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.f_softboot.toggle(True)
        self.cubesat.watchdog_pet()
        self.safe_sleep(120)

        return True

    def long_hibernate(self) -> Literal[True]:
        """Puts the Satellite to sleep for 180 seconds"""

        self.logger.debug("LONG Hibernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.f_softboot.toggle(True)
        self.cubesat.watchdog_pet()
        self.safe_sleep(600)

        return True
