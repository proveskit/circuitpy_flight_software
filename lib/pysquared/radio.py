import board
from adafruit_rfm import RFMSPI
from digitalio import DigitalInOut

from lib.adafruit_rfm import rfm9x, rfm9xfsk
from lib.pysquared.exception import NotInitializedError
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.flag import Flag

try:
    from typing import Literal
except ImportError:
    pass


class Radio:
    @classmethod
    def create(
        cls,
        use_fsk: Flag,
        logger: Logger,
        sender_id: int,
        receiver_id: int,
        transmit_frequency: int,
        transmit_power: int,
        lora_spreading_factor: int,
    ) -> RFMSPI:
        """Factory method to create radio instances.

        Args:
            radio_type: Type of radio to create ("lora" or "fsk")
            logger: Logger instance
            sender_id: Radio sender ID
            receiver_id: Radio receiver ID
            transmit_frequency: Radio frequency
            transmit_power: Transmit power (LoRa only)
            lora_spreading_factor: Spreading factor (LoRa only)

        Returns:
            Radio instance of specified type
        """
        chip_select_pin: DigitalInOut = DigitalInOut(board.SPI0_CS0)
        chip_select_pin.switch_to_output(value=True)

        reset_pin: DigitalInOut = DigitalInOut(board.RF1_RST)
        reset_pin.switch_to_output(value=True)

        radio_mode: Literal["fsk", "lora"] = "fsk" if use_fsk.get() else "lora"

        try:
            logger.debug(message="Initializing radio", mode=radio_mode)

            spi = "blah"  # TODO(nateinaction): fix me

            if use_fsk.get():
                radio: Radio = cls.create_fsk_radio(
                    spi,
                    chip_select_pin,
                    reset_pin,
                    transmit_frequency,
                )
            else:
                radio: Radio = cls.create_lora_radio(
                    spi,
                    chip_select_pin,
                    reset_pin,
                    transmit_frequency,
                    transmit_power,
                    lora_spreading_factor,
                )

            radio.node = sender_id
            radio.destination = receiver_id

            return radio
        except Exception as e:
            logger.critical("Failed to initialize radio", mode=radio_mode, err=e)

            raise NotInitializedError("radio", e)

    @staticmethod
    def create_fsk_radio(
        spi: any,  # TODO(nateinaction): fix me
        chip_select_pin: DigitalInOut,
        reset_pin: DigitalInOut,
        transmit_frequency: int,
    ) -> RFMSPI:
        radio: rfm9xfsk.RFM9xFSK = rfm9xfsk.RFM9xFSK(
            spi,
            chip_select_pin,
            reset_pin,
            transmit_frequency,
        )
        radio.fsk_node_address = 1
        radio.fsk_broadcast_address = 255
        radio.modulation_type

        return radio

    @staticmethod
    def create_lora_radio(
        spi: any,  # TODO(nateinaction): fix me
        chip_select_pin: DigitalInOut,
        reset_pin: DigitalInOut,
        transmit_frequency: int,
        transmit_power: int,
        lora_spreading_factor: int,
    ) -> RFMSPI:
        radio: rfm9x.RFM9x = rfm9x.RFM9x(
            spi,
            chip_select_pin,
            reset_pin,
            transmit_frequency,
        )
        radio.max_output = True
        radio.tx_power = transmit_power
        radio.spreading_factor = lora_spreading_factor

        radio.enable_crc = True
        radio.ack_delay = 0.2
        if radio.spreading_factor > 9:
            radio.preamble_length = radio.spreading_factor

        return radio
