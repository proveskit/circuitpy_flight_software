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
        self.state: OrderedDict[str, Any] = {
            # init all values to None
            "system_voltage": None,
            "system_current": None,
            "solar_voltage": None,
            "solar_current": None,
            "radio_temperature": None,
            "microcontroller_temperature": None,
            "internal_temperature": None,
            "error_count": None,
            "power_mode": None,
            "battery_voltage": None,
            "uptime": None,
            "boot_count": None,
            "battery_temperature": None,
            "burned_flag": None,
            "brownout_flag": None,
            "fsk_flag": None,
        }

    def update(self):
        """
        Update the state of health
        """
        try:
            # update IC20 related values
            if self.c.hardware["I2C0"]:
                self.state["system_voltage"] = self.c.micro.cpu.voltage
                self.state["system_current"] = self.c.charge_current
                self.state["solar_voltage"] = None # unsure on how to get these values
                self.state["solar_current"] = None   
                self.state["battery_temperature"] = self.f.last_battery_temp   
                self.state["battery_voltage"] = self.c.battery_voltage
            
            self.state["radio_temperature"] = self.f.last_radio_temp()
            self.state["microcontroller_temperature"] = self.c.micro.cpu.temperature
            self.state["internal_temperature"] = self.c.internal_temperature
            self.state["error_count"] = self.logger.get_error_count()
            self.state["power_mode"] = self.c.power_mode
            self.state["uptime"] = self.c.get_system_uptime
            self.state["boot_count"] = self.c.boot_count.get()
            self.state["burned_flag"] = self.c.f_burned.get()
            self.state["brownout_flag"] = self.c.f_brownout.get()
            self.state["fsk_flag"] = self.c.f_fsk.get()

        except Exception as e:
            self.logger.error("Couldn't acquire data for state of health", err=e)
        
        self.logger.info("State of Health", state=self.state)