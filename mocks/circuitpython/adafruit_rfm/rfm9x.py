"""
Mock for Adafruit RFM9x
https://github.com/adafruit/Adafruit_CircuitPython_RFM/blob/8a55e345501e038996b2aa89e71d4e5e3ddbdebe/adafruit_rfm/rfm9x.py
"""


class RFM9x:
    def __init__(self, spi, cs, reset, frequency):
        self.node = None
        self.destination = None
        self.ack_delay = None
        self.enable_crc = None
        self.max_output = None
        self.spreading_factor = None
        self.tx_power = None
        self.preamble_length = None
