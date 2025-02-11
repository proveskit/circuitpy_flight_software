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
