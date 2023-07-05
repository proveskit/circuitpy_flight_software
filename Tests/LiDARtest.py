import board
import busio
import time
import adafruit_vl6180x # LiDAR Distance Sensor for Antenna
import neopixel # RGB LED
i2c=busio.I2C(board.SCL1,board.SDA1)
# Initialize LiDAR
try:
    LiDAR = adafruit_vl6180x.VL6180X(i2c)
    LiDAR.offset=10
except Exception as e:
    print('[ERROR][LiDAR]' + str(e))
try:
    neopixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1,pixel_order=neopixel.GRB)
    neopixel[0]=(0,0,255)
except Exception as e:
    print('[ERROR][neopixel]' + str(e))
while True:
    print("Distance: ",LiDAR.range)

    time.sleep(1)