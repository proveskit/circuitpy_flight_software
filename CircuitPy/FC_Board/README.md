# flight_controller_software
Software for the flight controller board in the PROVES Kit. 
- **boot.py** This is the code that runs on boot and initializes the stack limit
- **cdh.py** This is the code that handles all the commands. A majority of this code is pulled from the cdh file developed by Max Holliday at Stanford.
- **code.py** This code runs the main operating system of the satellite and handles errors on a high level allowing the system to be fault tolerant
- **detumble.py** This code implements the B-dot algorithm and returns outputs that allow the system to do a controlled detumble with the satellite's embedded magnetourquer coils
- **main.py** This code tasks all the functions the satellite should do in a semi-asynchronous manner utilizing the asyncio library
- **payload.py** This code implements any desired payload. On the Pleiades missions, the payload has been the BNO055 IMU. Since the use of a stemmaQT connector allows multiple devices on the same bus, a BNO IMU could be used in conjunction with several other sensors if desired.
- **safemode.py** This code is unimplemented pending new firmware releases that allow the microconrtoller to perform a routine when in safemode
## experimental
This software is completely experimental and is in development for helpful software related tasks.
- **sf_hop.py** This code is yet to be implemented in official flight software as it is desired to implement the ability to utilize several spreading factors to send different sized messages at different data rates
## lib
This software contains all of the libraries required to operate the sensors, pysquared board, and radio module.
- **asyncio** This is the library responsible for scheduling tasks in the main code
- **adafruit_bno055.py** This is the library that is responsible for obtaining data from the BNO055 IMU
- **adafruit_drv2605.mpy** This is the pre-compiled library that is responsible for driving the magnetorquer coils using the drv2605 motor driver
- **adafruit_ina219.py** This is the library that is responsible for obtaining data from the INA219 Power Monitor
- **adafruit_mcp9808.mpy** This is the pre-compiled library that is responsible for obtaining data from the MCP9808 Temperature Sensor
- **adafruit_pca9685.py** This is the library that is responsible or driving the power to the satellite faces using the pca9685 LED driver
- **adafruit_tca9548a.mpy** This is the pre-compiled library that multiplexes the I2C line to each satellite face using the tca9548a I2C Multiplexer
- **adafruit_veml7700.py** This is the library that is responsible for obtaining data from the veml7700 Light Sensor
- **adafruit_vl6180.py** This is the library that is responsible for obtaining data from the vl6180 LiDAR sensor
- **Big_Data.py** This is a class developed to obtain data from the sensors on the 5 solar faces. Since all the faces maintain all the same sensors, this class handles the individual face sensors and returns them all to the main code.
- **bitflags.py** This is code that allows for some registers within the microcontroller to be written to and saved through power cycles
- **debugcolor.py** This is code that allows for easier debugging and is used by individual classes. Each class utilizes a different color and makes debugging substantially easier
- **Field.py** This is code that implements the radio module for sending and listening
- **functions.py** This is a library of functions utilized by the satellite to obtain data, detumble, run the battery heater
- **pysquared.py** This is a library that initializes and maintains all the main functions for the pysquared architecture
- **pysquared_rfm9x.py** This is a library that implements all the radio hardware. This code is a modified version of the pycubed_rfm9x which is a modified version of the adafruit_rfm9x file.
## tests
This software is used for performing tests on the satellite
