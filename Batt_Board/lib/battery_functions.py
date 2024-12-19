"""
This is the class that contains all of the functions for our CubeSat.
We pass the cubesat object to it for the definitions and then it executes
our will.
Authors: Nicole Maggard and Michael Pham 12/26/2023
"""

import time
import alarm
import gc
import traceback
from debugcolor import co  # pylint: disable=import-error

# Import for the CAN Bus Manager
from adafruit_mcp2515.canio import (
    Message,
    RemoteTransmissionRequest,
)  # pylint: disable=import-error


class functions:

    # Placeholders for the CAN Bus Manager
    FILE_IDS = {
        "file1": 0x01,
        "file2": 0x02,
        "file3": 0x03,
        # Add more files as needed
    }

    def debug_print(self, statement):
        if self.debug:
            print(co("[BATTERY][Functions]" + str(statement), "green", "bold"))

    def __init__(self, cubesat):
        self.cubesat = cubesat
        self.debug = cubesat.debug
        self.debug_print("Initializing Functionalities")
        self.error_count = 0
        self.face_id = 0x00AA
        self.facestring = []
        self.state_list = []
        self.last_battery_temp = 20
        self.state_bool = False
        self.detumble_enable_z = True
        self.detumble_enable_x = True
        self.detumble_enable_y = True
        try:
            self.cubesat.all_faces_on()
        except Exception as e:
            self.debug_print(
                "Couldn't turn faces on: " + "".join(traceback.format_exception(e))
            )  # pylint: disable=no-value-for-parameter
            self.cubesat.all_faces_off()

    # =======================================================#
    # Satellite Management Functions                        #
    # =======================================================#

    def battery_heater(self):
        """
        Battery Heater Function reads temperature at the end of the thermocouple and tries to
        warm the batteries until they are roughly +4C above what the batteries should normally sit(this
        creates a band stop in which the battery heater never turns off) The battery heater should not run
        forever, so a time based stop is implemented
        """
        try:
            try:
                self.last_battery_temp = self.cubesat.battery_temperature()
            except Exception as e:
                self.debug_print(
                    "[ERROR] couldn't get thermocouple data!"
                    + "".join(traceback.format_exception(e))
                )  # pylint: disable=no-value-for-parameter
                raise RuntimeError("Thermocouple failure!") from e

            if self.last_battery_temp < self.cubesat.NORMAL_BATT_TEMP:
                end_time = 0
                self.cubesat.heater_on()
                while (
                    self.last_battery_temp < self.cubesat.NORMAL_BATT_TEMP + 4
                    and end_time < 5
                ):
                    time.sleep(1)
                    self.last_battery_temp = self.cubesat.battery_temperature()
                    end_time += 1
                    self.debug_print(
                        str(
                            f"Heater has been on for {end_time} seconds and the battery temp is {self.last_battery_temp}C"
                        )
                    )
                return True

            else:
                self.debug_print("Battery is already warm enough")
                return False

        except Exception as e:
            self.debug_print(
                "Error Initiating Battery Heater"
                + "".join(traceback.format_exception(e))
            )  # pylint: disable=no-value-for-parameter
            return False
        finally:
            self.cubesat.heater_off()

    def current_check(self):
        return self.cubesat.current_draw

    def check_reboot(self):
        self.cubesat.UPTIME = self.cubesat.uptime
        self.debug_print(str("Current up time: " + str(self.cubesat.UPTIME)))
        if self.cubesat.UPTIME > 86400:
            self.cubesat.reset_vbus()

    def battery_manager(self):
        self.debug_print("Started to manage battery")
        try:
            vchrg = self.cubesat.charge_voltage
            vbatt = self.cubesat.battery_voltage
            ichrg = self.cubesat.charge_current
            idraw = self.cubesat.current_draw
            vsys = self.cubesat.system_voltage
            micro_temp = self.cubesat.micro.cpu.temperature

            self.debug_print("MICROCONTROLLER Temp: {} C".format(micro_temp))
            self.debug_print(
                f"Internal Temperature: {self.cubesat.internal_temperature} C"
            )
        except Exception as e:
            self.debug_print(
                "Error obtaining battery data: "
                + "".join(traceback.format_exception(e))
            )  # pylint: disable=no-value-for-parameter

        try:
            self.debug_print(f"charge current: {ichrg}mA, and charge voltage: {vbatt}V")
            self.debug_print(
                "draw current: {}mA, and battery voltage: {}V".format(idraw, vbatt)
            )
            self.debug_print("system voltage: {}V".format(vsys))

            # This check is currently unused, just a notification for debugging
            if idraw > ichrg:
                self.debug_print(
                    "Beware! The Satellite is drawing more power than receiving"
                )

            if vbatt < self.cubesat.CRITICAL_BATTERY_VOLTAGE:
                self.powermode("crit")
                self.debug_print(
                    "CONTEXT SHIFT INTO CRITICAL POWER MODE: Attempting to shutdown ALL systems..."
                )

            elif vbatt < self.cubesat.NORMAL_BATTERY_VOLTAGE:
                self.powermode("low")
                self.debug_print(
                    "CONTEXT SHIFT INTO LOW POWER MODE: Attempting to shutdown unnecessary systems..."
                )

            elif vbatt > self.cubesat.NORMAL_BATTERY_VOLTAGE + 0.5:
                self.powermode("max")
                self.debug_print(
                    "CONTEXT SHIFT INTO MAXIMUM POWER MODE: Attempting to revive all systems..."
                )

            elif (
                vbatt < self.cubesat.NORMAL_BATTERY_VOLTAGE + 0.3
                and self.cubesat.power_mode == "maximum"
            ):  # We are passing data in a weird way here, please check
                self.powermode("norm")
                self.debug_print(
                    "CONTEXT SHIFT INTO NORMAL POWER MODE: Attempting to revive necessary systems..."
                )

        except Exception as e:
            self.debug_print(
                "Error in Battery Manager: " + "".join(traceback.format_exception(e))
            )  # pylint: disable=no-value-for-parameter

    def powermode(self, mode):
        """
        Configure the hardware for minimum or normal power consumption
        Add custom modes for mission-specific control
        """
        try:
            if "crit" in mode:
                self.cubesat.neopixel.brightness = 0
                self.cubesat.enable_rf.value = False
                self.cubesat.power_mode = "critical"

            elif "low" in mode:
                self.cubesat.neopixel.brightness = 0
                self.cubesat.enable_rf.value = False
                self.cubesat.power_mode = "low"

            elif "norm" in mode:
                self.cubesat.enable_rf.value = True
                self.cubesat.power_mode = "normal"
                # don't forget to reconfigure radios, gps, etc...

            elif "max" in mode:
                self.cubesat.enable_rf.value = True
                self.cubesat.power_mode = "maximum"

        except Exception as e:
            self.debug_print(
                "Error in changing operations of powermode: "
                + "".join(traceback.format_exception(e))
            )  # pylint: disable=no-value-for-parameter

    # =======================================================#
    # State of Health Functions                             #
    # =======================================================#

    def state_of_health(self):
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
                f"AT:{self.cubesat.internal_temperature}",
                f"BT:{self.last_battery_temp}",
                f"BO:{int(self.cubesat.f_brownout)}",
            ]
        except Exception as e:
            self.debug_print(
                "Couldn't aquire data for the state of health: "
                + "".join(traceback.format_exception(e))
            )  # pylint: disable=no-value-for-parameter
        try:
            self.debug_print("Sending Face Data to FC")
            self.send_can(self.state_list)
        except Exception as e:
            self.debug_print(
                "Error Sending data over CAN bus"
                + "".join(traceback.format_exception(e))
            )  # pylint: disable=no-value-for-parameter

    # =======================================================#
    # Big Data Functions                                    #
    # =======================================================#
    def face_toggle(self, face, state):
        dutycycle = 0x0000
        if state:
            duty_cycle = 0xFFFF

        if face == "Face0":
            self.cubesat.Face0.duty_cycle = duty_cycle
        elif face == "Face1":
            self.cubesat.Face0.duty_cycle = duty_cycle
        elif face == "Face2":
            self.cubesat.Face0.duty_cycle = duty_cycle
        elif face == "Face3":
            self.cubesat.Face0.duty_cycle = duty_cycle
        elif face == "Face4":
            self.cubesat.Face0.duty_cycle = duty_cycle
        elif face == "Face5":
            self.cubesat.Face0.duty_cycle = duty_cycle

    def get_imu_data(self):

        self.cubesat.all_faces_on()
        data = (0, 0, 0)
        try:
            self.debug_print("Attempting to get data from Flight Controller")
            data = self.get_CAN("IMU")
        except Exception as e:
            self.debug_print(
                "Error retrieving IMU data" + "".join(traceback.format_exception(e))
            )

        return data

    # =======================================================#
    # Interboard Communitication Functions                 #
    # =======================================================#

    def send_face(self):
        try:
            self.debug_print("Sending Face Data to FC")
            for x in self.facestring:
                self.send_can(self.face_id, x)
        except Exception as e:
            self.debug_print(
                "Error Sending data over CAN bus"
                + "".join(traceback.format_exception(e))
            )  # pylint: disable=no-value-for-parameter

    # Example of how the calling class might handle the result
    # can_helper = CanBusHelper(can_bus, owner, debug)
    #
    # result = can_helper.listen_messages(timeout=5)
    # if result is not None:
    #    if result['type'] == 'RTR':
    #        # Handle Remote Transmission Request
    #        data_to_send = retrieve_data_based_on_rtr_id(result['id'])
    #        can_helper.send_can("DATA_RESPONSE", data_to_send)
    #    elif result['type'] == 'FAULT':
    #        # Handle Fault Message
    #        handle_fault(result['content'])

    def send_can(self, id, messages):
        if not isinstance(messages, list):
            messages = [messages]  # If messages is not a list, make it a list
        try:
            for message in messages:
                message = str(message)
                if isinstance(message, str):
                    byte_message = bytes(message, "UTF-8")
                else:
                    byte_message = bytes(message)
                self.cubesat.can_bus.send(Message(id, byte_message))
                self.debug_print("Sent CAN message: " + str(message))
        except Exception as e:
            self.debug_print(
                "Error Sending data over CAN bus"
                + "".join(traceback.format_exception(None, e, e.__traceback__))
            )  # pylint: disable=no-value-for-parameter

    # Made by CoPilot - Probably Not Working
    def listen_can_messages(self):
        with self.cubesat.can_bus.listen(timeout=1.0) as listener:
            message_count = listener.in_waiting()
            self.debug_print(str(message_count) + " messages available")
            for _i in range(message_count):
                msg = listener.receive()
                self.debug_print("Message from " + hex(msg.id))

                # We aren't sure if isinstance checks currently work
                if isinstance(msg, Message):
                    self.debug_print("message data: " + str(msg.data))
                if isinstance(msg, RemoteTransmissionRequest):
                    self.debug_print("RTR length: " + str(msg.length))
                    # Here you can process the RTR request
                    # For example, you might send a response with the requested data
                    response_data = self.get_data_for_rtr(msg.id)
                    if isinstance(response_data, list):
                        response_messages = [
                            Message(id=msg.id, data=data, extended=True)
                            for data in response_data
                        ]
                    else:
                        response_messages = [
                            Message(id=msg.id, data=response_data, extended=True)
                        ]
                    self.cubesat.send_can(response_messages)

    def get_data_for_rtr(self, id):

        if id == 0x01:  # Replace with the actual ID for all_face_data
            all_face_data = bytes(
                self.all_face_data()
            )  # This should return a bytes object
            messages = []
            start_message = Message(id=0x01, data=b"start", extended=True)
            messages.append(start_message)
            for i in range(0, len(all_face_data), 8):
                chunk = all_face_data[i : i + 8]
                message = Message(id=0x02, data=chunk, extended=True)
                messages.append(message)
            stop_message = Message(id=0x03, data=b"stop", extended=True)
            messages.append(stop_message)
            return messages

        elif id == 0x02:  # Replace with the actual ID for sensor 2
            return self.get_sensor_2_data()
        elif id == 0x03:  # Replace with the actual ID for sensor 3
            return self.get_sensor_3_data()
        else:
            # Default case if no matching ID is found
            return bytes([0x01, 0x02, 0x03, 0x04])

    def request_file(self, file_id, timeout=5.0):
        # Send RTR for the file
        rtr = RemoteTransmissionRequest(id=file_id)
        self.cubesat.can_bus.send(rtr)

        # Listen for response and reconstruct the file
        file_data = bytearray()
        start_time = time.monotonic()
        while True:
            if time.monotonic() - start_time > timeout:
                raise TimeoutError("No response received for file request")
            msg = self.cubesat.can_bus.receive()
            if msg is None:
                continue  # No message received, continue waiting
            if isinstance(msg, Message) and msg.id == file_id:
                if msg.data == b"start":
                    continue
                elif msg.data == b"stop":
                    break
                else:
                    file_data.extend(msg.data)
        return file_data

    def OTA(self):
        # resets file system to whatever new file is received
        pass

    # =======================================================#
    # Misc Functions                                        #
    # =======================================================#

    # Should be nuke the detumble function from this file?
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
                    data = self.get_imu_data()
                    data[0] = list(data[0])
                    for x in range(3):
                        if data[0][x] < 0.01:
                            data[0][x] = 0.0
                    data[0] = tuple(data[0])
                    dipole = detumble.magnetorquer_dipole(data[1], data[0])
                    self.debug_print("Dipole: " + str(dipole))
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
        self.cubesat.all_faces_off()
        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot = True
        time.sleep(120)
        self.cubesat.all_faces_on()
        self.cubesat.enable_rf.value = True
        return True

    def Long_Hybernate(self):
        self.debug_print("LONG Hybernation Coming UP")
        gc.collect()
        # all should be off from cubesat powermode
        self.cubesat.all_faces_off()
        self.cubesat.enable_rf.value = False
        self.cubesat.f_softboot = True
        time.sleep(600)
        self.cubesat.all_faces_on()
        self.cubesat.enable_rf.value = True
        return True
