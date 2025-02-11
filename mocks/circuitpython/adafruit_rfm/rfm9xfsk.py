class RFM9xFSK:
    def __init__(self, spi, cs, reset, frequency):
        self.fsk_broadcast_address = None
        self.fsk_node_address = None
        self.modulation_type = None
