# This is where the magic happens!
# This file is executed on every boot (including wake-boot from deepsleep)
# Created By: Michael Pham

"""
Built for the PySquared FC Board
Version: 2.0.0 
Published: Nov 19, 2024
"""

import time
import microcontroller

print("=" * 70)
print("Hello World!")
print("PySquared FC Board Circuit Python Software Version: 2.0.0")
print("Published: November 19, 2024")
print("=" * 70)

loiter_time = 5

try:
    for i in range(loiter_time):
        print(f"Code Starting in {loiter_time-i} seconds")
        time.sleep(1)

    import main

except Exception as e:
    print(e)
