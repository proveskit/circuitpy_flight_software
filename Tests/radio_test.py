# radio_test.py
# V1.0 June 24, 2024
# Authored by: Michael Pham

# The is a test script to facilitate a simple ping pong style communications test between two radios.

import time
from pysquared import cubesat
from time import sleep

test_message = "Hello There!"
debug_mode = True
number_of_attempts = 0

# Radio Configuration Setup Here
radio_cfg = {
    "spreading_factor": 8,
    "tx_power": 13,  # Set as a default that works for any radio
    "node": 0x00,
    "destination": 0x00,
    "receive_timeout": 5,
    "enable_crc": False,
}

options = ["A", "B", "C"]

# Setting the Radio
cubesat.radio1.spreading_factor = radio_cfg["spreading_factor"]
if cubesat.radio1.spreading_factor > 8:
    cubesat.radio1.low_datarate_optimize = True
else:
    cubesat.radio1.low_datarate_optimize = False
cubesat.radio1.tx_power = radio_cfg["tx_power"]
cubesat.radio1.receive_timeout = radio_cfg["receive_timeout"]
cubesat.radio1.enable_crc = False

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


def debug_print(message):
    if debug_mode:
        print(message)


def device_under_test(attempts):

    debug_print("Device Under Test Selected")
    debug_print("Setting up Radio...")

    cubesat.radio1.node = 0xFA
    cubesat.radio1.destination = 0xFF

    debug_print("Radio Setup Complete")
    debug_print("Sending Ping...")

    print(f"Attempt: {attempts}")
    cubesat.radio1.send(test_message)

    debug_print("Ping Sent")
    debug_print("Awaiting Response...")

    heard_something = cubesat.radio1.await_rx(timeout=10)

    if heard_something:
        handle_ping()

    else:
        debug_print("No Response Received")

        cubesat.radio1.send("Nothing Received")
        debug_print("Echo Sent")


def receiver():

    debug_print("Receiver Selected")
    debug_print("Setting up Radio...")

    cubesat.radio1.node = 0xFF
    cubesat.radio1.destination = 0xFA

    debug_print("Radio Setup Complete")
    debug_print("Awaiting Ping...")

    heard_something = cubesat.radio1.await_rx(timeout=10)

    if heard_something:
        handle_ping()

    else:
        debug_print("No Ping Received")

        cubesat.radio1.send("Nothing Received")
        debug_print("Echo Sent")


def client(passcode):
    debug_print("Client Selected")
    debug_print("Setting up radio")

    cubesat.radio1.node = 0xFA
    cubesat.radio1.destination = 0xFB

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
        packet = b"\x00\x00\x00\x00" + passcode.encode() + b"8\x93" + input("Query: ")
    elif chosen_command == "5":
        packet = (
            b"\x00\x00\x00\x00" + passcode.encode() + b"\x96\xa2" + input("Command: ")
        )
    elif chosen_command == "6":
        packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\xa5\xb4"
    elif chosen_command == "7":
        packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\x56\xc4"
    else:
        print(
            "Command is not valid or not implemented open radio_test.py and add them yourself!"
        )

    tries = 0
    while True:
        sleep(0.1)
        tries += 1
        if tries > 5:
            print("We tried 5 times! And there was no response. Quitting.")
            return
        cubesat.radio1.send(packet)
        response = cubesat.radio1.receive(keep_listening=True)

        if response is not None:
            print("msg: {}, RSSI: {}".format(response, cubesat.radio1.last_rssi - 137))
            return
        else:
            debug_print("No response, trying again (" + str(tries) + ")")


def handle_ping():
    response = cubesat.radio1.receive(keep_listening=True)

    if response is not None:
        debug_print("Ping Received")
        print("msg: {}, RSSI: {}".format(response, cubesat.radio1.last_rssi - 137))

        cubesat.radio1.send(
            "Ping Received! Echo:{}".format(cubesat.radio1.last_rssi - 137)
        )
        debug_print("Echo Sent")
    else:
        debug_print("No Ping Received")

        cubesat.radio1.send("Nothing Received")
        debug_print("Echo Sent")


device_selection = input()

if device_selection not in options:
    print("Invalid Selection.")
    print("Please refresh the device and try again.")

else:
    print(
        """ 
    ======================================= 
    |                                     | 
    |       Verbose Output? (Y/N)         |
    |                                     |
    =======================================
    """
    )

    verbose_selection = input()

    if verbose_selection == "Y":
        debug_mode = True
    elif verbose_selection == "N":
        debug_mode = False

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
        time.sleep(1)
        device_under_test(number_of_attempts)
        number_of_attempts += 1
    elif device_selection == "B":
        time.sleep(1)
        receiver()
    elif device_selection == "C":
        client(passcode)
        time.sleep(1)
