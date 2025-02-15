from lib.pysquared.functions import functions
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite


class StateOfHealth:
    def __init__(self, c, logger: Logger, f: functions):
        self.c: Satellite = c
        self.logger: Logger = logger
        self.f: functions = f
        self.state: dict = {}

    def update_state_of_health(self):
        """
        Update the state of health
        """
        self.logger.debug("Updating State of Health")
        self.state = {
            "system_voltage": self.c.micro.cpu.voltage,
            "system_current": self.c.charge_current,
            "solar_voltage": None,
            "solar_current": None,
            "radio_temperature": self.f.last_radio_temp(),
            "microcontroller_temperature": self.c.micro.cpu.temperature,
            "internal_temperature": None, # self.c.internal_temperature doesn't seem to work
            "error_count": self.logger.get_error_count(),
        }
        self.logger.info("State of Health", state=self.state)
