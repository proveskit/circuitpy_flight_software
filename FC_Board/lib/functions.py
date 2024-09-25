"""
This is the class that contains all of the functions for our CubeSat. 
We pass the cubesat object to it for the definitions and then it executes 
our will.
Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

import time
import alarm
import gc
import traceback
import random
from debugcolor import co


class functions:

    def debug_print(self, statement):
        if self.debug:
            print(co("[Functions]" + str(statement), "green", "bold"))

    def __init__(self, cubesat):
        self.cubesat = cubesat
        self.debug = cubesat.debug
        self.debug_print("Initializing Functionalities")
        self.Errorcount = 0
        self.facestring = []
        self.jokes = [
            "Hey Its pretty cold up here, did someone forget to pay the electric bill?"
        ]
        self.last_battery_temp = 20
        self.callsign = "Callsign"
        self.state_bool = False
        self.face_data_baton = False
        self.detumble_enable_z = True
        self.detumble_enable_x = True
        self.detumble_enable_y = True

    """
    Satellite Management Functions
    """

    def current_check(self):
        return self.cubesat.current_draw

    """
    Radio Functions
    """

    def send(self, msg):
        """Calls the RFM9x to send a message. Currently only sends with default settings.

        Args:
            msg (String,Byte Array): Pass the String or Byte Array to be sent.
        """
        import Field

        self.field = Field.Field(self.cubesat, self.debug)
        message = f"{self.callsign} " + str(msg) + f" {self.callsign}"
        self.field.Beacon(message)
        if self.cubesat.f_fsk:
            self.cubesat.radio1.cw(message)
        if self.cubesat.is_licensed:
            self.debug_print(f"Sent Packet: " + message)
        else:
            self.debug_print("Failed to send packet")
        del self.field
        del Field

    def beacon(self):
        """Calls the RFM9x to send a beacon."""
        import Field

        try:
            lora_beacon = (
                f"{self.callsign} Hello I am Yearling^2! I am in: "
                + str(self.cubesat.power_mode)
                + " power mode. V_Batt = "
                + str(self.cubesat.battery_voltage)
                + f"V. IHBPFJASTMNE! {self.callsign}"
            )
        except Exception as e:
            self.debug_print(
                "Error with obtaining power data: "
                + "".join(traceback.format_exception(e))
            )
            lora_beacon = (
                f"{self.callsign} Hello I am Yearling^2! I am in: "
                + "an unidentified"
                + " power mode. V_Batt = "
                + "Unknown"
                + f". IHBPFJASTMNE! {self.callsign}"
            )

        self.field = Field.Field(self.cubesat, self.debug)
        self.field.Beacon(lora_beacon)
        if self.cubesat.f_fsk:
            self.cubesat.radio1.cw(lora_beacon)
        del self.field
        del Field

    def joke(self):
        self.send(random.choice(self.jokes))

    def state_of_health(self):
        import Field

        self.state_list = []
        # list of state information
        try:
            self.state_list = [
                f"PM:{self.cubesat.power_mode}",
                f"VB:{self.cubesat.battery_voltage}",
                f"ID:{self.cubesat.current_draw}",
                f"IC:{self.cubesat.charge_current}",
                f"VS:{self.cubesat.system_voltage}",
                f"UT:{self.cubesat.uptime}",
                f"BN:{self.cubesat.c_boot}",
                f"MT:{self.cubesat.micro.cpu.temperature}",
                f"RT:{self.cubesat.radio1.former_temperature}",
                f"AT:{self.cubesat.internal_temperature}",
                f"BT:{self.last_battery_temp}",
                f"AB:{int(self.cubesat.burned)}",
                f"BO:{int(self.cubesat.f_brownout)}",
                f"FK:{int(self.cubesat.f_fsk)}",
            ]
        except Exception as e:
            self.debug_print(
                "Couldn't aquire data for the state of health: "
                + "".join(traceback.format_exception(e))
            )

        self.field = Field.Field(self.cubesat, self.debug)
        if not self.state_bool:
            self.field.Beacon(
                f"{self.callsign} Yearling^2 State of Health 1/2"
                + str(self.state_list)
                + f"{self.callsign}"
            )
            if self.cubesat.f_fsk:
                self.cubesat.radio1.cw(
                    f"{self.callsign} Yearling^2 State of Health 1/2"
                    + str(self.state_list)
                    + f"{self.callsign}"
                )
            self.state_bool = True
        else:
            self.field.Beacon(
                f"{self.callsign} YSOH 2/2"
                + str(self.cubesat.hardware)
                + f"{self.callsign}"
            )
            if self.cubesat.f_fsk:
                self.cubesat.radio1.cw(
                    f"{self.callsign} YSOH 2/2"
                    + str(self.cubesat.hardware)
                    + f"{self.callsign}"
                )
            self.state_bool = False
        del self.field
        del Field

    def send_face(self):
        """Calls the data transmit function from the field class"""
        import Field

        self.field = Field.Field(self.cubesat, self.debug)
        self.debug_print("Sending Face Data")
        self.field.Beacon(
            f"{self.callsign} Y-: {self.facestring[0]} Y+: {self.facestring[1]} X-: {self.facestring[2]} X+: {self.facestring[3]}  Z-: {self.facestring[4]} {self.callsign}"
        )
        if self.cubesat.f_fsk:
            self.cubesat.radio1.cw(
                f"{self.callsign} Y-: {self.facestring[0]} Y+: {self.facestring[1]} X-: {self.facestring[2]} X+: {self.facestring[3]}  Z-: {self.facestring[4]} {self.callsign}"
            )
        del self.field
        del Field

    def listen(self):
        import cdh

        # This just passes the message through. Maybe add more functionality later.
        try:
            self.debug_print("Listening")
            self.cubesat.radio1.receive_timeout = 10
            received = self.cubesat.radio1.receive(keep_listening=True)
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

    def listen_joke(self):
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

    def all_face_data(self):

        # self.cubesat.all_faces_on()
        try:
            print("New Function Needed!")

        except Exception as e:
            self.debug_print("Big_Data error" + "".join(traceback.format_exception(e)))

        return self.facestring

    def get_imu_data(self):

        try:
            data = []
            data.append(self.cubesat.IMU.Acceleration)
            data.append(self.cubesat.IMU.Gyroscope)
            data.append(self.cubesat.IMU.Magnetometer)
        except Exception as e:
            self.debug_print(
                "Error retrieving IMU data" + "".join(traceback.format_exception(e))
            )

        return data

    def OTA(self):
        # resets file system to whatever new file is received
        pass

    """
    Logging Functions
    """

    def log_face_data(self, data):

        self.debug_print("Logging Face Data")
        try:
            self.cubesat.log("/faces.txt", data)
        except:
            try:
                self.cubesat.new_file("/faces.txt")
            except Exception as e:
                self.debug_print("SD error: " + "".join(traceback.format_exception(e)))

    def log_error_data(self, data):

        self.debug_print("Logging Error Data")
        try:
            self.cubesat.log("/error.txt", data)
        except:
            try:
                self.cubesat.new_file("/error.txt")
            except Exception as e:
                self.debug_print("SD error: " + "".join(traceback.format_exception(e)))

    """
    Misc Functions
    """

    # Goal for torque is to make a control system
    # that will adjust position towards Earth based on Gyro data
    def detumble(self, dur=7, margin=0.2, seq=118):
        self.debug_print("Detumbling")
        self.cubesat.RGB = (255, 255, 255)
        self.cubesat.all_faces_on()
        try:
            import Big_Data

            a = Big_Data.AllFaces(self.debug, self.cubesat.tca)
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

        def actuate(dipole, duration):
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

        def do_detumble():
            try:
                import detumble

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

    def Short_Hybernate(self):
        self.debug_print("Short Hybernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot = True
        time.sleep(120)

        self.cubesat.enable_rf.value = True
        return True

    def Long_Hybernate(self):
        self.debug_print("LONG Hybernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode

        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot = True
        time.sleep(600)

        self.cubesat.enable_rf.value = True
        return True
