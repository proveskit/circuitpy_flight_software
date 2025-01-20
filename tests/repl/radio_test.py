# radio_test.py
# V1.0 June 24, 2024
# Authored by: Michael Pham

# The is a test script to facilitate a simple ping pong style communications test between two radios.

import time

from lib.pysquared.pysquared import Satellite


class RadioTest:
    number_of_attempts = 0
    test_message = "Hello There!"

    def __init__(
        self,
        config,
        cubesat: Satellite,
        fsk_or_lora: str,  # Either "f" for FSK or "l" for LoRa
    ):
        self.debug_mode = config["debug"]
        self.callsign = config["callsign"]

        if self.callsign == "":
            print("No cube callsign! Radio will not function")
            exit()

        self.cubesat = cubesat

        cubesat.f_fsk = True if fsk_or_lora == "fsk" else False

        radio_cfg = {
            "spreading_factor": 8,
            "tx_power": 13,  # Set as a default that works for any radio
            "node": 0x00,
            "destination": 0x00,
            "receive_timeout": 5,
            "enable_crc": False,
        }
        self.cubesat.radio1.spreading_factor = radio_cfg["spreading_factor"]
        if self.cubesat.radio1.spreading_factor > 8:
            self.cubesat.radio1.low_datarate_optimize = True
        else:
            self.cubesat.radio1.low_datarate_optimize = False
        self.cubesat.radio1.tx_power = radio_cfg["tx_power"]
        self.cubesat.radio1.receive_timeout = radio_cfg["receive_timeout"]
        self.cubesat.radio1.enable_crc = False

    def debug_print(self, message):
        if self.debug_mode:
            print(message)

    def device_under_test(self, attempts):
        self.debug_print("Device Under Test Selected")
        self.debug_print("Setting up Radio...")

        self.cubesat.radio1.node = 0xFA
        self.cubesat.radio1.destination = 0xFB

        self.debug_print("Radio Setup Complete")
        self.debug_print("Sending Ping...")

        print(f"Attempt: {attempts}")
        self.cubesat.radio1.send(self.test_message)

        self.debug_print("Ping Sent")
        self.debug_print("Awaiting Response...")

        heard_something = self.cubesat.radio1.receive(timeout=10)

        if heard_something:
            self.handle_ping()

        else:
            self.debug_print("No Response Received")

            self.cubesat.radio1.send("Nothing Received")
            self.debug_print("Echo Sent")

    def receiver(self):
        self.debug_print("Receiver Selected")
        self.debug_print("Setting up Radio...")

        self.cubesat.radio1.node = 0xFA
        self.cubesat.radio1.destination = 0xFB

        self.debug_print("Radio Setup Complete")
        self.debug_print("Awaiting Ping...")

        heard_something = self.cubesat.radio1.receive(timeout=10)

        if heard_something:
            self.handle_ping()

        else:
            self.debug_print("No Ping Received")

            self.cubesat.radio1.send("Nothing Received")
            self.debug_print("Echo Sent")

    def client(self, passcode):
        self.debug_print("Client Selected")
        self.debug_print("Setting up radio")

        self.cubesat.radio1.node = 0xFA
        self.cubesat.radio1.destination = 0xFB

        print(
            """
        =============== /\\ ===============
        = Please select command  :)      =
        ==================================
        1 - noop                         |
        2 - hreset                       |
        3 - shutdown                     |
        4 - query                        |
        5 - exec_cmd                     |
        6 - joke_reply                   |
        7 - FSK                          |
        8 - Repeat Code                  |
        ==================================
        """
        )

        chosen_command = input("Select cmd pls: ")

        packet = b""

        if chosen_command == "1":
            packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\x8eb"
        elif chosen_command == "2":
            packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\xd4\x9f"
        elif chosen_command == "3":
            packet = (
                b"\x00\x00\x00\x00" + passcode.encode() + b"\x12\x06" + b"\x0b\xfdI\xec"
            )
        elif chosen_command == "4":
            packet = b"\x00\x00\x00\x00" + passcode.encode() + b"8\x93" + input()
        elif chosen_command == "5":
            packet = (
                b"\x00\x00\x00\x00"
                + passcode.encode()
                + b"\x96\xa2"
                + input("Command: ")
            )
        elif chosen_command == "6":
            packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\xa5\xb4"
        elif chosen_command == "7":
            packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\x56\xc4"
        elif chosen_command == "8":
            packet = (
                b"\x00\x00\x00\x00"
                + passcode.encode()
                + b"RP"
                + input("Message to Repeat: ")
            )
        else:
            print(
                "Command is not valid or not implemented open radio_test.py and add them yourself!"
            )

        tries = 0
        while True:
            msg = self.cubesat.radio1.receive()

            if msg is not None:
                msg_string = "".join([chr(b) for b in msg])
                print(f"Message Received {msg_string}")

                time.sleep(0.1)
                tries += 1
                if tries > 5:
                    print("We tried 5 times! And there was no response. Quitting.")
                    break
                success = self.cubesat.radio1.send_with_ack(packet)
                print("Success " + str(success))
                if success is True:
                    print("Sending response")
                    response = self.cubesat.radio1.receive(keep_listening=True)
                    time.sleep(0.5)

                    if response is not None:
                        print(
                            "msg: {}, RSSI: {}".format(
                                response, self.cubesat.radio1.last_rssi - 137
                            )
                        )
                        break
                    else:
                        self.debug_print(
                            "No response, trying again (" + str(tries) + ")"
                        )

    def handle_ping(self):
        response = self.cubesat.radio1.receive(keep_listening=True)

        if response is not None:
            self.debug_print("Ping Received")
            print(
                "msg: {}, RSSI: {}".format(
                    response, self.cubesat.radio1.last_rssi - 137
                )
            )

            self.cubesat.radio1.send(
                "Ping Received! Echo:{}".format(self.cubesat.radio1.last_rssi - 137)
            )
            self.debug_print("Echo Sent")
        else:
            self.debug_print("No Ping Received")

            self.cubesat.radio1.send("Nothing Received")
            self.debug_print("Echo Sent")

    def run(self):
        options = ["A", "B", "C"]

        print(
            """
        =======================================
        |                                     |
        |              WELCOME!               |
        |       Radio Test Version 1.0        |
        |                                     |
        =======================================
        |       Please Select Your Node       |
        | 'A': Device Under Test              |
        | 'B': Receiver                       |
        ================ OR ===================
        |      Act as a client                |
        | 'C': for an active satalite         |
        =======================================
        """
        )

        device_selection = input()

        if device_selection not in options:
            print("Invalid Selection.")
            print("Please refresh the device and try again.")

        print(
            """
        =======================================
        |                                     |
        |        Beginning Radio Test         |
        |       Radio Test Version 1.0        |
        |                                     |
        =======================================
        """
        )

        passcode = ""
        if device_selection == "C":
            passcode = input(
                "What's the passcode (in plain text, will automagically be converted to UTF-8): "
            )

        while True:
            if device_selection == "A":
                self.number_of_attempts += 1
                if self.number_of_attempts >= 5:
                    print("Too many attempts. Quitting.")
                    break
                time.sleep(1)
                self.device_under_test(self.number_of_attempts)
            elif device_selection == "B":
                time.sleep(1)
                self.receiver()
            elif device_selection == "C":
                self.client(passcode)
                time.sleep(1)
