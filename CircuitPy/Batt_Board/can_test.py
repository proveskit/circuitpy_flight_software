from pysquared_eps import cubesat as c
import battery_functions
import can_bus_helper
import time

f = battery_functions.functions(c)

cb = can_bus_helper.CanBusHelper(c.can_bus, f, True)

while True:
    cb.listen_messages()
    time.sleep(1)
    print("Listened to messages")
