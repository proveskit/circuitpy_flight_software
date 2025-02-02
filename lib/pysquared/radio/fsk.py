import board
from digitalio import DigitalInOut

from lib.adafruit_rfm import rfm9xfsk
from lib.pysquared.errors import NotInitializedError
from lib.pysquared.logger import Logger
from lib.pysquared.radio.base import Radio


class RadioFsk(Radio):
    mode = "fsk"

    def __init__(
        self,
        logger: Logger,
        sender_id: int,
        receiver_id: int,
        transmit_frequency: int,
    ) -> None:
        try:
            self._log = logger
            self._log.debug("Initializing radio", mode=self.mode)

            chip_select_pin: DigitalInOut = DigitalInOut(board.SPI0_CS0)
            chip_select_pin.switch_to_output(
                value=True
            )  # cs1 and rst1 are only used locally

            reset_pin: DigitalInOut = DigitalInOut(board.RF1_RST)
            reset_pin.switch_to_output(value=True)

            self.radio: rfm9xfsk.RFM9xFSK = rfm9xfsk.RFM9xFSK(
                self.spi0,
                chip_select_pin,
                reset_pin,
                transmit_frequency,
            )
            self.radio.fsk_node_address = 1
            self.radio.fsk_broadcast_address = 255
            self.radio.modulation_type = 0

            self.radio.node = sender_id
            self.radio.destination = receiver_id

            self._log.debug("Initialized radio", mode=self.mode)
        except Exception as e:
            self._log.critical("Failed to initialize radio", mode=self.mode, err=e)
            raise NotInitializedError("radio", e)
