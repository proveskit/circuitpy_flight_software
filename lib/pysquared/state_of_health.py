from lib.pysquared.functions import functions
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite

try:
    from typing import Any, OrderedDict
except Exception:
    pass


class StateOfHealth:
    def __init__(self, c: Satellite, logger: Logger, f: functions):
        self.c: Satellite = c
        self.logger: Logger = logger
        self.f: functions = f
        self.state: OrderedDict[str, Any] = {}

    def update_state_of_health(self):
        """
        Update the state of health
        """
        self.logger.debug("Updating State of Health")
        try:
            self.state = {
                # if IC20 is not enabled, we can't access this sensor, at least from what I can tell from this image: https://docs.proveskit.space/en/latest/core_documentation/hardware/images/fc_board_block.png
                "system_voltage": self.c.micro.cpu.voltage
                if self.c.hardware["I2C0"]
                else None,
                "system_current": self.c.charge_current
                if self.c.hardware["I2C0"]
                else None,
                "solar_voltage": None,  # not sure how to get these values
                "solar_current": None,
                "radio_temperature": self.f.last_radio_temp(),
                "microcontroller_temperature": self.c.micro.cpu.temperature,
                "internal_temperature": None,  # self.c.internal_temperature doesn't seem to work
                "error_count": self.logger.get_error_count(),
                # stuff from old state_of_health function
                "power_mode": self.c.power_mode,
                "battery_voltage": self.c.battery_voltage
                if self.c.hardware["I2C0"]
                else None,
                "uptime": self.c.uptime,
                "boot_count": self.c.boot_count.get(),
                "battery_temperature": self.f.last_battery_temp
                if self.c.hardware["I2C0"]
                else None,  # this value is never actually calculated, just retrieved from config
                "burned_flag": self.c.f_burned.get(),
                "brownout_flag": self.c.f_brownout.get(),
                "fsk_flag": self.c.f_fsk.get(),
            }
            self.logger.info("State of Health", state=self.state)
        except Exception as e:
            self.logger.error("Couldn't acquire data for state of health", err=e)
