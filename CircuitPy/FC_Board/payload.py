"""
payload.py
This file contains all software to handle whatever payload the intended satellite contains
Yearling-2 contains simply a bno085 9 DOF sensor that is being implemented in this software
Author: Nicole Maggard
"""

import time
import board
import busio
import traceback
from debugcolor import co
import adafruit_bno055


class PAYLOAD:
    def debug_print(self, statement):
        if self.debug:
            print(co("[Payload]" + statement, "gray", "bold"))

    def Enable(self, data):
        self.debug_print("Enabling the following: " + str(data))
        if "acceleration" in data:
            from adafruit_bno08x import BNO_REPORT_ACCELEROMETER

            self.bno.enable_feature(BNO_REPORT_ACCELEROMETER)
            self.acceleration = (0, 0, 0)
        if "gyroscope" in data:
            from adafruit_bno08x import BNO_REPORT_GYROSCOPE

            self.bno.enable_feature(BNO_REPORT_GYROSCOPE)
            self.gyroscope = (0, 0, 0)
        if "magnetometer" in data:
            from adafruit_bno08x import BNO_REPORT_MAGNETOMETER

            self.bno.enable_feature(BNO_REPORT_MAGNETOMETER)
            self.magnetometer = (0, 0, 0)
        if "linear acceleration" in data:
            from adafruit_bno08x import BNO_REPORT_LINEAR_ACCELERATION

            self.bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
            self.linear_acceleration = (0, 0, 0)
        if "rotation vector" in data:
            from adafruit_bno08x import BNO_REPORT_ROTATION_VECTOR

            self.bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
            self.rotation = (0, 0, 0)
        if "geomagnetic rotation vector" in data:
            from adafruit_bno08x import BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR

            self.bno.enable_feature(BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR)
            self.geomagnetic_rotation = (0, 0, 0)
        if "game rotation vector" in data:
            from adafruit_bno08x import BNO_REPORT_GAME_ROTATION_VECTOR

            self.bno.enable_feature(BNO_REPORT_GAME_ROTATION_VECTOR)
            self.game_rotation = (0, 0, 0)
        if "raw acceleration" in data:
            from adafruit_bno08x import BNO_REPORT_RAW_ACCELEROMETER

            self.bno.enable_feature(BNO_REPORT_RAW_ACCELEROMETER)
            self.raw_acceleration = (0, 0, 0)
        if "raw gyroscope" in data:
            from adafruit_bno08x import BNO_REPORT_RAW_GYROSCOPE

            self.bno.enable_feature(BNO_REPORT_RAW_GYROSCOPE)
            self.raw_gyroscope = (0, 0, 0)
        if "raw magnetometer" in data:
            from adafruit_bno08x import BNO_REPORT_RAW_MAGNETOMETER

            self.bno.enable_feature(BNO_REPORT_RAW_MAGNETOMETER)
            self.raw_magnetometer = (0, 0, 0)

    def __init__(self, debug, i2c, data=[]):
        self.debug = debug
        self.data = data
        self.debug_print("Initializing BNO055...")
        try:
            self.bno = adafruit_bno055.BNO055_I2C(i2c)
            self.debug_print("Initialization of BNO complete without error!")
        except Exception as e:
            self.debug_print(
                "ERROR Initializing BNO sensor: "
                + "".join(traceback.format_exception(e))
            )

    def reinit(self, data=[]):
        try:
            self.debug_print("Reinitializing BNO08x...")
            self.Enable(self.data)
            self.debug("Reinitialization of BNO complete without error!")
        except Exception as e:
            self.debug_print(
                "ERROR Initializing BNO sensor: "
                + "".join(traceback.format_exception(e))
            )

    @property
    def Data(self):
        return self.data

    def UpdateData(self, data, option="append"):
        if option == "replace":
            self.data = data
        if option == "append":
            self.data.append(data)
        else:
            raise TypeError(
                'Incorrect option argument input. Please use either "append" or "replace"'
            )
        self.reinit()

    @property
    def Acceleration(self):
        if "acceleration" in self.data:
            self.acceleration = self.bno.acceleration
        return self.acceleration

    @property
    def Gyroscope(self):
        if "gyroscope" in self.data:
            self.gyroscope = self.bno.gyro
        return self.gyroscope

    @property
    def Magnetometer(self):
        if "magnetometer" in self.data:
            self.magnetometer = self.bno.magnetic
        return self.magnetometer

    @property
    def Linear_Acceleration(self):
        if "linear acceleration" in self.data:
            self.linear_acceleration = self.bno.linear_acceleration
        return self.linear_acceleration

    @property
    def Rotation(self):
        if "rotation vector" in self.data:
            self.rotation = self.bno.quaternion
        return self.rotation

    @property
    def Geomagnetic_Rotation(self):
        if "geomagnetic rotation vector" in self.data:
            self.geomagnetic_rotation = self.bno.geomagnetic_quaternion
        return self.geomagnetic_rotation

    @property
    def Game_Rotation(self):
        if "game rotation vector" in self.data:
            self.game_rotation = self.bno.game_quaternion
        return self.game_rotation

    @property
    def Raw_Acceleration(self):
        if "raw acceleration" in self.data:
            self.raw_acceleration = self.bno.raw_acceleration
        return self.raw_acceleration

    @property
    def Raw_Gyroscope(self):
        if "raw gyroscope" in self.data:
            self.raw_gyroscope = self.bno.raw_gyro
        return self.raw_gyroscope

    @property
    def Raw_Magnetometer(self):
        if "raw magnetometer" in self.data:
            self.raw_magnetometer = self.bno.raw_magnetic
        return self.raw_magnetometer
