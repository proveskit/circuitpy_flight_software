import time
from pysquared import cubesat

class Field():

    def __init__(self):
        self.testMsg=[]
        self.testMsg.append("Hello There!")
        self.testMsg.append("I have brought peace, freedom, justice, and security to my new empire. Your new empire!?")
        self.testMsg.append("ahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
        self.cubesat=cubesat
        self.cubesat.enable_rf.value=True
        self.cubesat.radio1.spreading_factor=8
        self.cubesat.radio1.low_datarate_optimize=False
        self.cubesat.radio1.node=0xfb
        self.cubesat.radio1.destination=0xfa
        self.cubesat.radio1.receive_timeout=10
        self.cubesat.radio1.enable_crc=True
        self.cubesat.all_faces_off()

    def fieldSide(self,msg):
        print("Sending test message:")
        self.cubesat.radio1.send(self.testMsg[msg] + " SF: " + str(self.cubesat.radio1.spreading_factor), keep_listening=True)

        print("Listening for transmissions, {}s".format(self.cubesat.radio1.receive_timeout))
        heard_something = self.cubesat.radio1.await_rx(timeout=20)

        if heard_something:
            response = self.cubesat.radio1.receive(keep_listening=True)

            if response is not None:
                print("packet received")
                print('msg: {}, RSSI: {}'.format(response,self.cubesat.radio1.last_rssi-137))

            else:
                print("no packets received")
    
    def fieldrun(self,timeout=10,spread=8,msg=0):
        self.cubesat.radio1.receive_timeout=timeout
        self.cubesat.radio1.spreading_factor=spread
        if self.cubesat.radio1.spreading_factor>8:
            self.cubesat.radio1.low_datarate_optimize=True
        while True:
            self.fieldSide(msg)

test=Field()