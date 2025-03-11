import time

import serial

# ser = serial.Serial('/dev/tty.usbmodem1101')
# print(ser.name)

"""
with serial.Serial('/dev/tty.usbmodem1101', 9600, timeout=5) as ser:
    x = ser.read()          # read one byte
    s = ser.read(10)        # read up to ten bytes (timeout)
    line = ser.readlines()   # read a '\n' terminated line
    print(line)

"""

#'from lib.pysquared.rtc.rp2040 import RP2040RTC'

ser = serial.Serial("/dev/tty.usbmodem1101", 115200, timeout=10)

"""
while True:
    s = ser.read(1000)       # read up to one hundred bytes
                        # or as much is in the buffer
    lines = ser.readlines()
    for x in lines:
        print(x)
"""


def lol():
    repl_line_met = False
    while not repl_line_met:
        ser.write(b"\x03")
        # s = ser.read(10)
        lines = ser.readlines()

        for line in lines:
            print(line)
            if b"Press any key to enter the REPL" in line:
                repl_line_met = True
                ser.write(b"\r\n")

    adafruit_line_met = False
    while not adafruit_line_met:
        # s = ser.read(10)
        lines = ser.readlines()

        for line in lines:
            print(line)
            if (
                b"Adafruit CircuitPython 9.1.4-dirty on 2024-10-05; PySquaredFCv4 with rp2040"
                in line
            ):
                adafruit_line_met = True

    ser.write(b"import lib.pysquared.rtc.rp2040 as rp")
    ser.write(b"\r\n")
    current_time_stuct = time.localtime()
    update_time_string = (
        "rp.RP2040RTC.set_time({0}, {1}, {2}, {3}, {4}, {5}, {6})".format(
            current_time_stuct.tm_year,
            current_time_stuct.tm_mon,
            current_time_stuct.tm_mday,
            current_time_stuct.tm_hour,
            current_time_stuct.tm_min,
            current_time_stuct.tm_sec,
            current_time_stuct.tm_wday,
        )
    )
    result = update_time_string.encode()
    ser.write(result)
    ser.write(b"\r\n")
    ser.write(b"import supervisor")
    ser.write(b"\r\n")
    ser.write(b"supervisor.reload()")
    ser.write(b"\r\n")
