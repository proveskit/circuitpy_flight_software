from pysquared import cubesat as c
import functions
import can_bus_helper
import time

f = functions.functions(c)

cb = can_bus_helper.CanBusHelper(c.can_bus, f, True)

while True:
    cb.listen_messages()
    time.sleep(1)
    print("Listened to messages")
