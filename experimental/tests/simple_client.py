# SPDX-FileCopyrightText: 2023 ladyada
#
# SPDX-License-Identifier: MIT
#!/usr/bin/env python3

"""
This example client runs on CPython and connects to / sends data to the
simpleserver example.
"""
import board
import busio
import digitalio
import time
import pysquared_w5500

print("Wiznet5k SimpleServer Test")

# For Adafruit Ethernet FeatherWing
cs = digitalio.DigitalInOut(board.D10)
# For Particle Ethernet FeatherWing
# cs = digitalio.DigitalInOut(board.D5)
spi_bus = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
MAC = (0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xEE)
# Initialize ethernet interface
eth = pysquared_w5500.WIZNET5500(spi_bus, cs,mac=MAC,debug=True)

# Initialize a socket for our server
pysquared_w5500.set_interface(eth)
print("Chip Version:", eth.chip)
print("A simple client for the wiznet5k_simpleserver.py example in this directory")
print(
    "Run this on any device connected to the same network as the server, after "
    "editing this script with the correct HOST & PORT\n"
)
# Or, use any TCP-based client that can easily send 1024 bytes. For example:
#     python -c 'print("1234"*256)' | nc 192.168.10.1 50007

time.sleep(1)

# edit host and port to match server
HOST = "48.48.67.48"
PORT = 50007
TIMEOUT = 10
INTERVAL = 5
MAXBUF = 1024
while True:
    s = pysquared_w5500.socket(pysquared_w5500.AF_INET, pysquared_w5500.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    print(f"Connecting to {HOST}:{PORT}")
    s.connect((HOST, PORT))
    # wiznet5k_simpleserver.py wants exactly 1024 bytes
    size = s.send(b"A5" * 512)
    print("Sent", size, "bytes")
    buf = s.recv(MAXBUF)
    print("Received", buf)
    s.close()
    time.sleep(INTERVAL)
