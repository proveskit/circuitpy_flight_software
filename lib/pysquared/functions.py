"""
This is the class that contains all of the functions for our CubeSat.
We pass the cubesat object to it for the definitions and then it executes
our will.
Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

import gc
import random
import time
import traceback

import alarm

from lib.pysquared.battery_helper import BatteryHelper
from lib.pysquared.config import Config
from lib.pysquared.debugcolor import co
from lib.pysquared.packet_manager import PacketManager
from lib.pysquared.packet_sender import PacketSender
from lib.pysquared.logger import Logger

try:
    from typing import Any, List, Literal, OrderedDict, Union

    import circuitpython_typing
except Exception:
    pass
from lib.pysquared.pysquared import Satellite


class functions:
    def debug_print(self, statement: Any) -> None:
        if self.debug:
            print(co("[Functions]" + str(statement), "green", "bold"))

    def __init__(self, cubesat: Satellite, logger: Logger, config: Config) -> None:
        self.logger = logger
        self.cubesat: Satellite = cubesat
        self.battery: BatteryHelper = BatteryHelper(cubesat)
        self.debug: bool = cubesat.debug
        self.debug_print("Initializing Functionalities")

        self.pm: PacketManager = PacketManager(max_packet_size=128)
        self.ps: PacketSender = PacketSender(cubesat.radio1, self.pm, max_retries=3)

        self.config: Config = config
        self.cubesatName: str = config.getStr("cubesatName")
        self.Errorcount: int = 0
        self.facestring: list = [None, None, None, None, None]
        self.jokes: list[str] = config.getList("jokes")
        self.last_battery_temp: float = config.getFloat("last_battery_temp")
        self.sleep_duration: int = config.getInt("sleep_duration")
        self.callsign: str = config.getStr("callsign")
        self.state_bool: bool = False
        self.face_data_baton: bool = False
        self.detumble_enable_z: bool = config.getBool("detumble_enable_z")
        self.detumble_enable_x: bool = config.getBool("detumble_enable_x")
        self.detumble_enable_y: bool = config.getBool("detumble_enable_y")

    """
    Satellite Management Functions
    """

    def current_check(self) -> float:
        return self.cubesat.current_draw

    def safe_sleep(self, duration: int = 15) -> None:
        self.debug_print("Setting Safe Sleep Mode")

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
        self.debug_print("Listening for 10 seconds")
        self.cubesat.watchdog_pet()
        self.cubesat.radio1.receive_timeout = 10
        self.listen()
        self.cubesat.watchdog_pet()

        self.debug_print("Sleeping for 20 seconds")
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

        self.field: Field.Field = Field.Field(self.cubesat, self.debug)
        message: str = f"{self.callsign} " + str(msg) + f" {self.callsign}"
        self.field.Beacon(message)
        if self.cubesat.is_licensed:
            self.debug_print("Sent Packet: " + message)
        else:
            self.debug_print("Failed to send packet")
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
                f"{self.callsign} Hello I am {self.cubesatName}! I am: "
                + str(self.cubesat.power_mode)
                + f" UT:{self.cubesat.uptime} BN:{self.cubesat.c_boot} EC:{self.cubesat.c_error_count} "
                + f"IHBPFJASTMNE! {self.callsign}"
            )
        except Exception as e:
            self.debug_print(
                "Error with obtaining power data: "
                + "".join(traceback.format_exception(e))
            )
            lora_beacon: str = (
                f"{self.callsign} Hello I am Yearling^2! I am in: "
                + "an unidentified"
                + " power mode. V_Batt = "
                + "Unknown"
                + f". IHBPFJASTMNE! {self.callsign}"
            )

        self.field: Field.Field = Field.Field(self.cubesat, self.debug)
        self.field.Beacon(lora_beacon)
        del self.field
        del Field
        gc.collect()

    def joke(self) -> None:
        self.send(random.choice(self.jokes))

    def last_radio_temp(self) -> int:
        """Tries to grab former temp from module"""
        raw_temp = self.cubesat.radio1.read_u8(0x5B)
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
                f"BN:{self.cubesat.c_boot}",
                f"MT:{self.cubesat.micro.cpu.temperature}",
                f"RT:{self.last_radio_temp()}",
                f"AT:{self.cubesat.internal_temperature}",
                f"BT:{self.last_battery_temp}",
                f"EC:{self.cubesat.c_error_count}",
                f"AB:{int(self.cubesat.burned)}",
                f"BO:{int(self.cubesat.f_brownout)}",
                f"FK:{int(self.cubesat.f_fsk)}",
            ]
        except Exception as e:
            self.debug_print(
                "Couldn't aquire data for the state of health: "
                + "".join(traceback.format_exception(e))
            )

        self.field: Field.Field = Field.Field(self.cubesat, self.debug)
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

        self.field: Field.Field = Field.Field(self.cubesat, self.debug)
        self.debug_print("Sending Face Data")
        self.field.Beacon(
            f"{self.callsign} Y-: {self.facestring[0]} Y+: {self.facestring[1]} X-: {self.facestring[2]} X+: {self.facestring[3]}  Z-: {self.facestring[4]} {self.callsign}"
        )
        del self.field
        del Field
        gc.collect()

    def listen(self) -> bool:
        # need to instanciate cdh to feed it the config var
        # assigned from the Config object
        from lib.pysquared.cdh import CommandDataHandler

        cdh = CommandDataHandler(self.config)

        # This just passes the message through. Maybe add more functionality later.
        try:
            self.debug_print("Listening")
            self.cubesat.radio1.receive_timeout = 10
            received = self.cubesat.radio1.receive_with_ack(keep_listening=True)
        except Exception as e:
            self.debug_print(
                "An Error has occured while listening: "
                + "".join(traceback.format_exception(e))
            )
            received = None

        try:
            if received is not None:
                self.debug_print("Recieved Packet: " + str(received))
                cdh.message_handler(self.cubesat, received)
                return True
        except Exception as e:
            self.debug_print(
                "An Error has occured while handling command: "
                + "".join(traceback.format_exception(e))
            )
        finally:
            del cdh

        return False

    def listen_joke(self) -> bool:
        try:
            self.debug_print("Listening")
            self.cubesat.radio1.receive_timeout = 10
            received = self.cubesat.radio1.receive(keep_listening=True)
            if received is not None and "HAHAHAHAHA!" in received:
                return True
            else:
                return False
        except Exception as e:
            self.debug_print(
                "An Error has occured while listening: "
                + "".join(traceback.format_exception(e))
            )
            received = None
            return False

    """
    Big_Data Face Functions
    change to remove fet values, move to pysquared
    """

    def all_face_data(self) -> list:
        # self.cubesat.all_faces_on()
        self.debug_print(gc.mem_free())
        gc.collect()

        try:
            import lib.pysquared.Big_Data as Big_Data

            self.debug_print(gc.mem_free())

            gc.collect()
            a: Big_Data.AllFaces = Big_Data.AllFaces(self.debug, self.cubesat.tca)
            self.debug_print(gc.mem_free())

            self.facestring: list = a.Face_Test_All()

            del a
            del Big_Data
            gc.collect()

        except Exception as e:
            self.debug_print("Big_Data error" + "".join(traceback.format_exception(e)))

        return self.facestring

    def get_battery_data(
        self,
    ) -> Union[tuple[float, float, float, float, bool, float], None]:
        try:
            return self.battery.get_power_metrics()

        except Exception as e:
            self.debug_print(
                "Error retrieving battery data" + "".join(traceback.format_exception(e))
            )
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
            self.debug_print(
                "Error retrieving IMU data" + "".join(traceback.format_exception(e))
            )

        return data

    def OTA(self) -> None:
        # resets file system to whatever new file is received
        self.debug_print("Implement an OTA Function Here")
        pass

    """
    Logging Functions
    """

    def log_face_data(self, data) -> None:
        self.debug_print("Logging Face Data")
        try:
            self.cubesat.log("/faces.txt", data)
        except Exception as e:
            self.debug_print("SD error: " + "".join(traceback.format_exception(e)))

    def log_error_data(self, data) -> None:
        self.debug_print("Logging Error Data")
        try:
            self.cubesat.log("/error.txt", data)
        except Exception as e:
            self.debug_print("SD error: " + "".join(traceback.format_exception(e)))

    """
    Misc Functions
    """

    # Goal for torque is to make a control system
    # that will adjust position towards Earth based on Gyro data
    def detumble(self, dur: int = 7, margin: float = 0.2, seq: int = 118) -> None:
        self.debug_print("Detumbling")
        self.cubesat.RGB = (255, 255, 255)

        try:
            import lib.pysquared.Big_Data as Big_Data

            a: Big_Data.AllFaces = Big_Data.AllFaces(self.debug, self.cubesat.tca)
        except Exception as e:
            self.debug_print(
                "Error Importing Big Data: " + "".join(traceback.format_exception(e))
            )

        try:
            a.sequence = 52
        except Exception as e:
            self.debug_print(
                "Error setting motor driver sequences: "
                + "".join(traceback.format_exception(e))
            )

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
                    self.debug_print("Dipole: " + str(dipole))
                    self.send("Detumbling! Gyro, Mag: " + str(data))
                    time.sleep(1)
                    actuate(dipole, dur)
            except Exception as e:
                self.debug_print(
                    "Detumble error: " + "".join(traceback.format_exception(e))
                )

        try:
            self.debug_print("Attempting")
            do_detumble()
        except Exception as e:
            self.debug_print(
                "Detumble error: " + "".join(traceback.format_exception(e))
            )
        self.cubesat.RGB = (100, 100, 50)

    def Short_Hybernate(self) -> Literal[True]:
        self.debug_print("Short Hybernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot = True
        self.safe_sleep(120)

        self.cubesat.enable_rf.value = True
        return True

    def Long_Hybernate(self) -> Literal[True]:
        self.debug_print("LONG Hybernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot = True
        self.safe_sleep(600)

        self.cubesat.enable_rf.value = True
        return True
