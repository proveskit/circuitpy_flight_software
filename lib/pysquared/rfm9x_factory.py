from busio import SPI
from digitalio import DigitalInOut
from machine import Pin

from lib.adafruit_rfm.rfm9x import RFM9x
from lib.adafruit_rfm.rfm9xfsk import RFM9xFSK
from lib.adafruit_rfm.rfm_common import RFMSPI
from lib.pysquared.exception import HardwareInitializationError
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.flag import Flag


class RFM9xMode:
    """Enumeration for the RFM9x radio mode."""

    FSK = "fsk"
    LORA = "lora"


class RFM9xFactory:
    """Factory class for creating RFM9x radio instances."""

    @classmethod
    def create(
        cls,
        logger: Logger,
        spi: SPI,
        chip_select: Pin,
        reset: Pin,
        use_fsk: Flag,
        sender_id: int,
        receiver_id: int,
        frequency: int,
        transmit_power: int,
        lora_spreading_factor: int,
    ) -> RFMSPI:
        """Create a RFM9x radio instance.

        :param Logger logger: Logger instance for logging messages.
        :param busio.SPI spi: The SPI bus connected to the chip. Ensure SCK, MOSI, and MISO are connected.
        :param ~digitalio.DigitalInOut cs: A DigitalInOut object connected to the chip's CS/chip select line.
        :param ~digitalio.DigitalInOut reset: A DigitalInOut object connected to the chip's RST/reset line.
        :param Flag use_fsk: Flag to determine whether to use FSK or LoRa mode.
        :param int sender_id: ID of the sender radio.
        :param int receiver_id: ID of the receiver radio.
        :param int frequency: Frequency at which the radio will transmit.
        :param int transmit_power: Transmit power level (applicable for LoRa only).
        :param int lora_spreading_factor: Spreading factor for LoRa modulation (applicable for LoRa only).

        :raises HardwareInitializationError: If the radio fails to initialize.

        :return An instance of the RFMSPI class, either RFM9xFSK or RFM9x based on the mode.
        """
        try:
            logger.debug(message="Initializing radio", mode=cls.radio_mode(use_fsk))

            cs: DigitalInOut = DigitalInOut(chip_select)
            cs.switch_to_output(value=True)

            rst: DigitalInOut = DigitalInOut(reset)
            rst.switch_to_output(value=True)

            if use_fsk.get():
                radio: RFMSPI = cls.create_fsk_radio(
                    spi,
                    cs,
                    rst,
                    frequency,
                )
            else:
                radio: RFMSPI = cls.create_lora_radio(
                    spi,
                    cs,
                    rst,
                    frequency,
                    transmit_power,
                    lora_spreading_factor,
                )

            radio.node = sender_id
            radio.destination = receiver_id

            return radio
        except Exception as e:
            logger.critical(
                "Failed to initialize radio", mode=cls.radio_mode(use_fsk), err=e
            )

            raise HardwareInitializationError("radio", e)

    @staticmethod
    def radio_mode(use_fsk: Flag) -> str:
        """Get the radio mode based on the flag.

        :param Flag use_fsk: Flag to determine whether to use FSK or LoRa mode.

        :return The radio mode.
        """
        return RFM9xMode.FSK if use_fsk.get() else RFM9xMode.LORA

    @staticmethod
    def create_fsk_radio(
        spi: SPI,
        cs: DigitalInOut,
        rst: DigitalInOut,
        frequency: int,
    ) -> RFMSPI:
        """Create a FSK radio instance.

        :param busio.SPI spi: The SPI bus connected to the chip. Ensure SCK, MOSI, and MISO are connected.
        :param ~digitalio.DigitalInOut cs: A DigitalInOut object connected to the chip's CS/chip select line.
        :param ~digitalio.DigitalInOut reset: A DigitalInOut object connected to the chip's RST/reset line.
        :param int frequency: Frequency at which the radio will transmit.

        :return An instance of :class:`~adafruit_rfm.rfm9xfsk.RFM9xFSK`.
        """
        radio: RFM9xFSK = RFM9xFSK(
            spi,
            cs,
            rst,
            frequency,
        )

        radio.fsk_broadcast_address = 255
        radio.fsk_node_address = 1
        radio.modulation_type

        return radio

    @staticmethod
    def create_lora_radio(
        spi: SPI,
        cs: DigitalInOut,
        rst: DigitalInOut,
        frequency: int,
        transmit_power: int,
        lora_spreading_factor: int,
    ) -> RFMSPI:
        """Create a LoRa radio instance.

        :param busio.SPI spi: The SPI bus connected to the chip. Ensure SCK, MOSI, and MISO are connected.
        :param ~digitalio.DigitalInOut cs: A DigitalInOut object connected to the chip's CS/chip select line.
        :param ~digitalio.DigitalInOut reset: A DigitalInOut object connected to the chip's RST/reset line.
        :param int frequency: Frequency at which the radio will transmit.
        :param int transmit_power: Transmit power level (applicable for LoRa only).
        :param int lora_spreading_factor: Spreading factor for LoRa modulation (applicable for LoRa only).

        :return An instance of the RFM9x class.
        """
        radio: RFM9x = RFM9x(
            spi,
            cs,
            rst,
            frequency,
        )

        radio.ack_delay = 0.2
        radio.enable_crc = True
        radio.max_output = True
        radio.spreading_factor = lora_spreading_factor
        radio.tx_power = transmit_power

        if radio.spreading_factor > 9:
            radio.preamble_length = radio.spreading_factor

        return radio
