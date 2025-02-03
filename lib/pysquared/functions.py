"""
This is the class that contains all of the functions for our CubeSat.
We pass the cubesat object to it for the definitions and then it executes
our will.
Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

import gc
import random
import time

import alarm

from lib.adafruit_rfm.rfm_common import RFMSPI
from lib.pysquared.battery_helper import BatteryHelper
from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.packet_manager import PacketManager
from lib.pysquared.packet_sender import PacketSender
from lib.pysquared.pysquared import Satellite

try:
    from typing import List, Literal, OrderedDict, Union

    import circuitpython_typing
except Exception:
    pass


class functions:
    def __init__(
        self, logger: Logger, config: Config, cubesat: Satellite, radio: RFMSPI
    ) -> None:
        self.logger = logger
        self.cubesat: Satellite = cubesat
        self.battery: BatteryHelper = BatteryHelper(cubesat, logger)
        self._radio: RFMSPI = radio
        self.logger.info("Initializing Functionalities")

        self.pm: PacketManager = PacketManager(logger=self.logger, max_packet_size=128)
        self.ps: PacketSender = PacketSender(
            self.logger, self._radio, self.pm, max_retries=3
        )

        self.config: Config = config
        self.cubesat_name: str = config.get_str("cubesat_name")
        self.Errorcount: int = 0
        self.facestring: list = [None, None, None, None, None]
        self.jokes: list[str] = config.get_list("jokes")
        self.last_battery_temp: float = config.get_float("last_battery_temp")
        self.sleep_duration: int = config.get_int("sleep_duration")
        self.callsign: str = config.get_str("callsign")
        self.state_bool: bool = False
        self.face_data_baton: bool = False
        self.detumble_enable_z: bool = config.get_bool("detumble_enable_z")
        self.detumble_enable_x: bool = config.get_bool("detumble_enable_x")
        self.detumble_enable_y: bool = config.get_bool("detumble_enable_y")

    """
    Satellite Management Functions
    """

    def current_check(self) -> float:
        return self.cubesat.current_draw

    def safe_sleep(self, duration: int = 15) -> None:
        self.logger.info("Setting Safe Sleep Mode")

        iterations: int = 0

        while duration > 15 and iterations < 12:
            time_alarm: circuitpython_typing.Alarm = alarm.time.TimeAlarm(
                monotonic_time=time.monotonic() + 15
            )

            alarm.light_sleep_until_alarms(time_alarm)
            duration -= 15
            iterations += 1

            self.cubesat.watchdog_pet()

    def listen_loiter(self) -> None:
        self.logger.debug("Listening for 10 seconds")
        self.cubesat.watchdog_pet()
        self._radio.receive_timeout = 10
        self.listen()
        self.cubesat.watchdog_pet()

        self.logger.debug("Sleeping for 20 seconds")
        self.cubesat.watchdog_pet()
        self.safe_sleep(self.sleep_duration)
        self.cubesat.watchdog_pet()

    """
    Radio Functions
    """

    def send(self, msg: Union[str, bytearray]) -> None:
        """Calls the RFM9x to send a message. Currently only sends with default settings.

        Args:
            msg (String,Byte Array): Pass the String or Byte Array to be sent.
        """
        import lib.pysquared.Field as Field

        self.field: Field.Field = Field.Field(self.logger, self.cubesat, self._radio)
        message: str = f"{self.callsign} " + str(msg) + f" {self.callsign}"
        self.field.Beacon(message)
        if self.cubesat.is_licensed:
            self.logger.debug("Sent Packet", packet_message=message)
        else:
            self.logger.warning("Failed to send packet")
        del self.field
        del Field
        gc.collect()

    def send_packets(self, data: Union[str, bytearray]) -> None:
        """Sends packets of data over the radio with delay between packets.

        Args:
            data (String, Byte Array): Pass the data to be sent.
            delay (float): Delay in seconds between packets
        """
        self.ps.send_data(data)

    def beacon(self) -> None:
        """Calls the RFM9x to send a beacon."""
        import lib.pysquared.Field as Field

        try:
            lora_beacon: str = (
                f"{self.callsign} Hello I am {self.cubesat_name}! I am: "
                + str(self.cubesat.power_mode)
                + f" UT:{self.cubesat.uptime} BN:{self.cubesat.boot_count.get()} EC:{self.logger.get_error_count()} "
                + f"IHBPFJASTMNE! {self.callsign}"
            )
        except Exception as e:
            self.logger.error("Error with obtaining power data: ", err=e)

            lora_beacon: str = (
                f"{self.callsign} Hello I am Yearling^2! I am in: "
                + "an unidentified"
                + " power mode. V_Batt = "
                + "Unknown"
                + f". IHBPFJASTMNE! {self.callsign}"
            )

        self.field: Field.Field = Field.Field(self.logger, self.cubesat, self._radio)
        self.field.Beacon(lora_beacon)
        del self.field
        del Field
        gc.collect()

    def joke(self) -> None:
        self.send(random.choice(self.jokes))

    def last_radio_temp(self) -> int:
        """Tries to grab former temp from module"""
        raw_temp = self._radio.read_u8(0x5B)
        temp = raw_temp & 0x7F
        if (raw_temp & 0x80) == 0x80:
            temp = ~temp + 0x01

        return temp + 143  # Added prescalar for temp

    def format_state_of_health(self, hardware: OrderedDict[str, bool]) -> str:
        to_return: str = ""
        for key, value in hardware.items():
            to_return = to_return + key + "="
            if value:
                to_return += "1"
            else:
                to_return += "0"

            if len(to_return) > 245:
                return to_return

        return to_return

    def state_of_health(self) -> None:
        import lib.pysquared.Field as Field

        self.state_list: list = []
        # list of state information
        try:
            self.state_list: list = [
                f"PM:{self.cubesat.power_mode}",
                f"VB:{self.cubesat.battery_voltage}",
                f"ID:{self.cubesat.current_draw}",
                f"IC:{self.cubesat.charge_current}",
                f"UT:{self.cubesat.uptime}",
                f"BN:{self.cubesat.boot_count.get()}",
                f"MT:{self.cubesat.micro.cpu.temperature}",
                f"RT:{self.last_radio_temp()}",
                f"AT:{self.cubesat.internal_temperature}",
                f"BT:{self.last_battery_temp}",
                f"EC:{self.logger.get_error_count()}",
                f"AB:{int(self.cubesat.f_burned.get())}",
                f"BO:{int(self.cubesat.f_brownout.get())}",
                f"FK:{int(self.cubesat.f_fsk.get())}",
            ]
        except Exception as e:
            self.logger.error("Couldn't aquire data for the state of health: ", err=e)

        self.field: Field.Field = Field.Field(self.logger, self.cubesat, self._radio)
        if not self.state_bool:
            self.field.Beacon(
                f"{self.callsign} Yearling^2 State of Health 1/2"
                + str(self.state_list)
                + f"{self.callsign}"
            )
            self.state_bool: bool = True
        else:
            self.field.Beacon(
                f"{self.callsign} YSOH 2/2"
                + self.format_state_of_health(self.cubesat.hardware)
                + f"{self.callsign}"
            )
            self.state_bool: bool = False
        del self.field
        del Field
        gc.collect()

    def send_face(self) -> None:
        """Calls the data transmit function from the field class"""
        import lib.pysquared.Field as Field

        self.field: Field.Field = Field.Field(self.logger, self.cubesat, self._radio)
        self.logger.debug("Sending Face Data")
        self.field.Beacon(
            f"{self.callsign} Y-: {self.facestring[0]} Y+: {self.facestring[1]} X-: {self.facestring[2]} X+: {self.facestring[3]}  Z-: {self.facestring[4]} {self.callsign}"
        )
        del self.field
        del Field
        gc.collect()

    def listen(self) -> bool:
        # need to instantiate cdh to feed it the config var
        # assigned from the Config object
        from lib.pysquared.cdh import CommandDataHandler

        cdh = CommandDataHandler(self.logger, self.config, self._radio)

        # This just passes the message through. Maybe add more functionality later.
        try:
            self.logger.debug("Listening")
            self._radio.receive_timeout = 10
            received = self._radio.receive_with_ack(keep_listening=True)
        except Exception as e:
            self.logger.error("An Error has occured while listening: ", err=e)
            received = None

        try:
            if received is not None:
                self.logger.debug("Received Packet", packet=received)
                cdh.message_handler(self.cubesat, received)
                return True
        except Exception as e:
            self.logger.error("An Error has occured while handling a command: ", err=e)
        finally:
            del cdh

        return False

    def listen_joke(self) -> bool:
        try:
            self.logger.debug("Listening")
            self._radio.receive_timeout = 10
            received = self._radio.receive(keep_listening=True)
            if received is not None and "HAHAHAHAHA!" in received:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error("An Error has occured while listening for a joke", err=e)
            received = None
            return False

    """
    Big_Data Face Functions
    change to remove fet values, move to pysquared
    """

    def all_face_data(self) -> list:
        # self.cubesat.all_faces_on()
        self.logger.debug(
            "Free Memory Stat at beginning of all_face_data function",
            bytes_free=gc.mem_free(),
        )
        gc.collect()

        try:
            import lib.pysquared.Big_Data as Big_Data

            self.logger.debug(
                "Free Memory Stat after importing Big_data library",
                bytes_free=gc.mem_free(),
            )

            gc.collect()
            a: Big_Data.AllFaces = Big_Data.AllFaces(self.cubesat.tca, self.logger)
            self.logger.debug(
                "Free Memory Stat after initializing All Faces object",
                bytes_free=gc.mem_free(),
            )

            self.facestring: list = a.Face_Test_All()

            del a
            del Big_Data
            gc.collect()

        except Exception as e:
            self.logger.error("Big_Data error", err=e)

        return self.facestring

    def get_battery_data(
        self,
    ) -> Union[tuple[float, float, float, float, bool, float], None]:
        try:
            return self.battery.get_power_metrics()

        except Exception as e:
            self.logger.error("Error retrieving battery data", err=e)
            return None

    def get_imu_data(
        self,
    ) -> List[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]:
        try:
            data: list = []
            data.append(self.cubesat.accel)
            data.append(self.cubesat.gyro)
            data.append(self.cubesat.mag)
        except Exception as e:
            self.logger.error("Error retrieving IMU data", err=e)

        return data

    def OTA(self) -> None:
        # resets file system to whatever new file is received
        self.logger.debug("Implement an OTA Function Here")
        pass

    """
    Misc Functions
    """

    # Goal for torque is to make a control system
    # that will adjust position towards Earth based on Gyro data
    def detumble(self, dur: int = 7, margin: float = 0.2, seq: int = 118) -> None:
        self.logger.debug("Detumbling")
        self.cubesat.RGB = (255, 255, 255)

        try:
            import lib.pysquared.Big_Data as Big_Data

            a: Big_Data.AllFaces = Big_Data.AllFaces(self.cubesat.tca, self.logger)
        except Exception as e:
            self.logger.error("Error Importing Big Data", err=e)

        try:
            a.sequence = 52
        except Exception as e:
            self.logger.error("Error setting motor driver sequences", err=e)

        def actuate(dipole: list[float], duration) -> None:
            # TODO figure out if there is a way to reverse direction of sequence
            if abs(dipole[0]) > 1:
                a.Face2.drive = 52
                a.drvx_actuate(duration)
            if abs(dipole[1]) > 1:
                a.Face0.drive = 52
                a.drvy_actuate(duration)
            if abs(dipole[2]) > 1:
                a.Face4.drive = 52
                a.drvz_actuate(duration)

        def do_detumble() -> None:
            try:
                import lib.pysquared.detumble as detumble

                for _ in range(3):
                    data = [self.cubesat.IMU.Gyroscope, self.cubesat.IMU.Magnetometer]
                    data[0] = list(data[0])
                    for x in range(3):
                        if data[0][x] < 0.01:
                            data[0][x] = 0.0
                    data[0] = tuple(data[0])
                    dipole = detumble.magnetorquer_dipole(data[1], data[0])
                    self.logger.debug("Detumbling", dipole=dipole)
                    self.send("Detumbling! Gyro, Mag: " + str(data))
                    time.sleep(1)
                    actuate(dipole, dur)
            except Exception as e:
                self.logger.error("Detumble error", err=e)

        try:
            self.logger.debug("Attempting")
            do_detumble()
        except Exception as e:
            self.logger.error("Detumble error", err=e)
        self.cubesat.RGB = (100, 100, 50)

    def Short_Hybernate(self) -> Literal[True]:
        self.logger.debug("Short Hybernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot.toggle(True)
        self.safe_sleep(120)

        self.cubesat.enable_rf.value = True
        return True

    def Long_Hybernate(self) -> Literal[True]:
        self.logger.debug("LONG Hybernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot.toggle(True)
        self.safe_sleep(600)

        self.cubesat.enable_rf.value = True
        return True
