import board
import busio
import time
import adafruit_pca9685, adafruit_tca9548a, adafruit_veml7700, adafruit_mcp9808, adafruit_drv2605, ina219
i2c=busio.I2C(board.SCL0,board.SDA0)
pca=adafruit_pca9685.PCA9685(i2c,address=86)
tca=adafruit_tca9548a.TCA9548A(i2c,address=119)
pca.frequency=60
pca.channels[0].duty_cycle=0xffff
pca.channels[1].duty_cycle=0xffff
veml0=adafruit_veml7700.VEML7700(tca[0])
mcp0=adafruit_mcp9808.MCP9808(tca[0],address=27)
drv0=adafruit_drv2605.DRV2605(tca[0])
veml1=adafruit_veml7700.VEML7700(tca[1])
mcp1=adafruit_mcp9808.MCP9808(tca[1],address=27)
try:
    drv1=adafruit_drv2605.DRV2605(tca[1])
except:
    drv1=adafruit_drv2605.DRV2605(tca[1],address=95)
ina=ina219.INA219(tca[5],addr=64)
drv0.sequence[0]=adafruit_drv2605.Effect(47)
drv1.sequence[0]=adafruit_drv2605.Effect(47)
while True:
    drv0.play()
    drv1.play()
    print("VEML7700 0: ",veml0.lux)
    print("MCP9808 0: ",mcp0.temperature)
    print("DRV2605 0: ",drv0.sequence[0])
    print("VEML7700 1: ",veml1.lux)
    print("MCP9808 1: ",mcp1.temperature)
    print("DRV2605 1: ",drv1.sequence[0])
    print("INA219: {:6.3f}V, {:7.4}mA, {:8.5}mW".format(ina.bus_voltage,ina.current,ina.power))
    time.sleep(1)
    drv0.stop()
    drv1.stop()
    time.sleep(1)