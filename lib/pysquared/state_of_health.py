from collections import OrderedDict

from lib.pysquared.functions import functions
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite
import gc

try:
    from typing import Any, OrderedDict
except Exception:
    pass


class StateOfHealth:
    def __init__(self, c: Satellite, logger: Logger, f: functions):
        self.c: Satellite = c
        self.logger: Logger = logger
        self.f: functions = f
        self.soh1: bool = False
        self.state: OrderedDict[str, Any] = OrderedDict(
            [
                # init all values in ordered dict to None
                ("system_voltage", None),
                ("system_current", None),
                ("solar_voltage", None),
                ("solar_current", None),
                ("battery_temperature", None),
                ("battery_voltage", None),
                ("radio_temperature", None),
                ("radio_modulation", None),
                ("microcontroller_temperature", None),
                ("internal_temperature", None),
                ("error_count", None),
                ("power_mode", None),
                ("uptime", None),
                ("boot_count", None),
                ("burned_flag", None),
                ("brownout_flag", None),
                ("fsk_flag", None)
            ]
        )

    def update(self):
        """
        Update the state of health
        """
        try:
            self.state["system_voltage"] = self.c.system_voltage
            self.state["system_current"] = self.c.current_draw
            self.state["solar_voltage"] = self.c.solar_voltage
            self.state["solar_current"] = self.c.charge_current
            self.state["battery_temperature"] = self.f.last_battery_temp # literally just gets a value from config  
            self.state["battery_voltage"] = self.c.battery_voltage
            self.state["radio_temperature"] = self.f.radio_manager.get_temperature()
            self.state["radio_modulation"] = self.f.radio_manager.get_modulation()
            self.state["microcontroller_temperature"] = self.c.micro.cpu.temperature
            self.state["internal_temperature"] = self.c.internal_temperature
            self.state["error_count"] = self.logger.get_error_count()
            self.state["power_mode"] = self.c.power_mode
            self.state["uptime"] = self.c.get_system_uptime
            self.state["boot_count"] = self.c.boot_count.get()
            self.state["burned_flag"] = self.c.f_burned.get()
            self.state["brownout_flag"] = self.c.f_brownout.get()

        except Exception as e:
            self.logger.error("Couldn't acquire data for state of health", err=e)
        
        self.logger.info("State of Health", state=self.state)