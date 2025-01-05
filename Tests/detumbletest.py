import time

import functions
from debugcolor import co
from pysquared import cubesat as c


def debug_print(statement):
    if c.debug:
        print(co("[MAIN]" + statement, "blue", "bold"))


f = functions.functions(c)
while True:
    f.detumble()
    f.send("Detumble finished")
    c.RGB = (255, 255, 0)
    time.sleep(5)
