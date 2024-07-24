# radio_test.py
# V1.0 June 24, 2024
# Authored by: Michael Pham

# The is a test script to facilitate a simple ping pong style communications test between two radios.

import time
from pysquared import cubesat

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

options = ["A", "B"]

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

while True:

    if device_selection == "A":
        time.sleep(1)
        device_under_test(number_of_attempts)
        number_of_attempts += 1
    elif device_selection == "B":
        time.sleep(1)
        receiver()
