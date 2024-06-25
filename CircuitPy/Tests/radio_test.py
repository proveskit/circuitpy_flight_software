# radio_test.py 
# V1.0 June 24, 2024
# Authored by: Michael Pham 

# The is a test script to facilitate a simple ping pong style communications test between two radios.

import time
from pysquared import cubesat

test_message = 'Hello There!'

# Radio Configuration Setup Here
radio_cfg = { 
    'spreading_factor': 8,
    'tx_power': 23,
    'node': 0x00,
    'destination': 0x00,
    'receive_timeout': 10,
    'enable_crc': False
}

# Setting the Radio
cubesat.radio1.spreading_factor=radio_cfg['spreading_factor']
if cubesat.radio1.spreading_factor>8:
    cubesat.radio1.low_datarate_optimize=True
else:
    cubesat.radio1.low_datarate_optimize=False
cubesat.radio1.tx_power=radio_cfg['tx_power']
cubesat.radio1.receive_timeout=radio_cfg['receive_timeout']
cubesat.radio1.enable_crc=False


print( 
''' 
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
'''
    )

device_selection = input()

if device_selection != 'A' or 'B':
    print("Invalid Selection.")
    print("Please refresh the device and try again.")

def device_under_test():

    print("Device Under Test Selected")
    print("Setting up Radio...")

    cubesat.radio1.node=0xfa
    cubesat.radio1.destination=0xff

    print("Radio Setup Complete")
    print("Sending Ping...")

    cubesat.radio1.send(test_message)

    print("Ping Sent")
    print("Awaiting Response...")

    heard_something = cubesat.radio1.await_rx(timeout=10)

    if heard_something:
        handle_ping()

    else:
        print("No Response Received")

        cubesat.radio1.send('Nothing Received')
        print("Echo Sent")

def receiver():

    print("Receiver Selected")
    print("Setting up Radio...")

    cubesat.radio1.node=0xff
    cubesat.radio1.destination=0xfa

    print("Radio Setup Complete")
    print("Awaiting Ping...")

    heard_something = cubesat.radio1.await_rx(timeout=10)

    if heard_something:
        handle_ping()

    else:
        print("No Ping Received")

        cubesat.radio1.send('Nothing Received')
        print("Echo Sent")

def handle_ping():
    response = cubesat.radio1.receive(keep_listening=True)

    if response is not None:
        print("Ping Received")
        print('msg: {}, RSSI: {}'.format(response,cubesat.radio1.last_rssi-137))

        cubesat.radio1.send('Ping Received! Echo:{}'.format(cubesat.radio1.last_rssi-137))
        print("Echo Sent")
    else:
        print("No Ping Received")

        cubesat.radio1.send('Nothing Received')
        print("Echo Sent")

    while True:
        print( 
        ''' 
        ======================================= 
        |                                     | 
        |        Beginning Radio Test         | 
        |       Radio Test Version 1.0        |
        |                                     |
        =======================================
        '''
            )
        if device_selection == 'A':
            time.sleep(1)
            device_under_test()
        if device_selection == 'B':
            time.sleep(1)
            receiver()
