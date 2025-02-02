import board
from digitalio import DigitalInOut

from lib.adafruit_rfm import rfm9x
from lib.pysquared.errors import NotInitializedError
from lib.pysquared.logger import Logger
from lib.pysquared.radio.base import Radio


class RadioLora(Radio):
    mode = "lora"
    spi0 = board.SPI()

    def __init__(
        self,
        logger: Logger,
        sender_id: int,
        receiver_id: int,
        transmit_frequency: int,
        transmit_power: int,
        lora_spreading_factor: int,
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

            self.radio: rfm9x.RFM9x = rfm9x.RFM9x(
                self.spi0,
                chip_select_pin,
                reset_pin,
                transmit_frequency,
            )
            self.radio.max_output = True
            self.radio.tx_power = transmit_power
            self.radio.spreading_factor = lora_spreading_factor

            self.radio.enable_crc = True
            self.radio.ack_delay = 0.2
            if self.radio.spreading_factor > 9:
                self.radio.preamble_length = self.radio.spreading_factor

            self.radio.node = sender_id
            self.radio.destination = receiver_id

            self._log.debug("Initialized radio", mode=self.mode)
        except Exception as e:
            self._log.critical("Failed to initialize radio", mode=self.mode, err=e)
            raise NotInitializedError("radio", e)
