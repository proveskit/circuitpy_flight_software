print("I am in safemode. Help!")
import microcontroller  # circuitpython module will need stub/mock for IDE intellesense, Issue #27
import time

time.sleep(10)
microcontroller.reset()
