'''
In this method the PyCubed will wait a pre-allotted loiter time before proceeding to execute
main. This loiter time is to allow for a keyboard interupt if needed. 

Authors: Nicole Maggard and Michael Pham
'''

import time
import microcontroller

try:
    import main

except Exception as e:    
    print(e)
    time.sleep(10)
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()