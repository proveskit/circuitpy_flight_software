import pysquared_rfm9x # Radio
import board
import digitalio
import time
import busio

device = "sat"

#Initialize SPI
spi = busio.SPI(board.SPI0_SCK,board.SPI0_MOSI,board.SPI0_MISO)

#Initialize the radio
_rf_cs1 = digitalio.DigitalInOut(board.SPI0_CS)
_rf_rst1 = digitalio.DigitalInOut(board.RF_RESET)
enable_rf = digitalio.DigitalInOut(board.ENABLE_RF)
radio1_DIO0=digitalio.DigitalInOut(board.RF_IO0)
radio1_DIO4=digitalio.DigitalInOut(board.RF_IO4)

enable_rf.direction = digitalio.Direction.OUTPUT
enable_rf.value = True

radio1 = pysquared_rfm9x.RFM9x(spi, _rf_cs1, _rf_rst1, frequency=437.4)
radio1.dio0 = radio1_DIO0
radio1.max_output = True
# set up LoRa spreading factors to try
spreading_factors = [7, 8, 9, 10, 11, 12]

timeout = 1

def find_spreading_factor():
    for spreading_factor in spreading_factors:
        # set LoRa spreading factor
        radio1.spreading_factor = spreading_factor
        if spreading_factor > 10:
            radio1.low_datarate_optimize = 0
            radio1.preamble_length = spreading_factor
            
            timeout = 3
        else:
            radio1.low_datarate_optimize = 0
            timeout = 1 
            radio1.preamble_length - 8
        print(f"Attempting Spreading Factor: {spreading_factor}")
        
        radio1.send("Hello World!")
        
        packet = radio1.receive(timeout=timeout)
        
        # check if LoRa module is receiving signals
        if packet is not None:
            print(f"Received packet on spreading factor: {spreading_factor}: {packet}, RSSI: {radio1.last_rssi-137}")
        else:
            print(f"No Device on Spreading Factor: {spreading_factor}")
            
def respond_to_ping():
    spreading_factor = 7
    radio1.spreading_factor = spreading_factor
    
    while True:
        packet = radio1.receive(timeout=timeout)
        if packet is not None:
            print(f"Received packet on spreading factor: {spreading_factor}: {packet}, RSSI: {radio1.last_rssi}")
            radio1.send("Good to see you!")
            
            if spreading_factor < 12:
                spreading_factor += 1
                radio1.spreading_factor = spreading_factor
                
            else:
                spreading_factor = 7
        else:
            print(f"No Device on Spreading Factor: {spreading_factor}")


while True:
    if device == "sat":
        find_spreading_factor()
    else:
        respond_to_ping()
    

    