import time
from pysquared import cubesat as c

print("=" * 70)
print("Initializing Simple Receiving Script")
print("=" * 70)

c.radio1.node = 0xFA
c.radio1.destination = 0xFB
c.radio1.enable_crc = False
c.radio1.spreading_factor = 8
c.radio1.coding_rate = 5

while True:
    
    print(f"Time[{time.monotonic()}] Received: {c.radio1.receive(keep_listening=True)} RSSI: {c.radio1.last_rssi}")

    time.sleep(1)