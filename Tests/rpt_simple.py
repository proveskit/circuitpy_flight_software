import time
from pysquared import cubesat as c

print("=" * 70)
print("Initializing Simple Repeater Commanding Script")
print("=" * 70)

c.radio1.node = 0xFA
c.radio1.destination = 0xFB
c.radio1.tx_power = 20
c.radio1.spreading_factor = 8
c.radio1.coding_rate = 5
passcode = ""

while True:

    packet = (
            b"\x00\x00\x00\x00"
            + passcode.encode()
            + b"RP"
            + input("Message to Repeat: ")
        )
    
    c.radio1.send(packet, keep_listening=True)

    time.sleep(1)

    print(f"{c.radio1.receive(keep_listening=True)} RSSI: {c.radio1.last_rssi}")