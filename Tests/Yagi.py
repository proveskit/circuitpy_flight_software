import time
from pysquared import cubesat

class Yagi():

    def __init__(self):
        self.cubesat=cubesat
        self.cubesat.radio1.spreading_factor=8
        self.cubesat.radio1.tx_power=23
        self.cubesat.radio1.low_datarate_optimize=False
        self.cubesat.radio1.node=0xfa
        self.cubesat.radio1.destination=0xff
        self.cubesat.radio1.receive_timeout=10
        self.cubesat.radio1.enable_crc=False
        if self.cubesat.radio1.spreading_factor>8:
            self.cubesat.radio1.low_datarate_optimize=True

    def yagiSide(self): 
        print("Listening for transmissions, {}s".format(self.cubesat.radio1.receive_timeout))
        heard_something = self.cubesat.radio1.await_rx(timeout=10)

        if heard_something:
            response = self.cubesat.radio1.receive(keep_listening=True)

            if response is not None:
                print("packet received")
                print('msg: {}, RSSI: {}'.format(response,self.cubesat.radio1.last_rssi-137))

                #self.cubesat.radio1.send('Received! Echo:{}'.format(self.cubesat.radio1.last_rssi-137))
                print("Echo sent")
            else:
                print("no packets received")

                #self.cubesat.radio1.send('Nothing Received')
                print("Echo sent")
    
    def yagirun(self,timeout=10,spread=8):
        self.cubesat.radio1.receive_timeout=timeout
        self.cubesat.radio1.spreading_factor=spread
        if self.cubesat.radio1.spreading_factor>8:
            self.cubesat.radio1.low_datarate_optimize=True
        while True:
            self.yagiSide()

test=Yagi()