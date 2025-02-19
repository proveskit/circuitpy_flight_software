from lib.pysquared.hardware.decorators import with_retries
from lib.pysquared.hardware.exception import HardwareInitializationError
from lib.pysquared.hardware.rfm9x.modulation import RFM9xModulation
from lib.pysquared.logger import Logger

try:
    from lib.adafruit_rfm.rfm9x import RFM9x
    from lib.adafruit_rfm.rfm9xfsk import RFM9xFSK
except ImportError:
    from mocks.circuitpython.adafruit_rfm.rfm9x import RFM9x  # type: ignore
    from mocks.circuitpython.adafruit_rfm.rfm9xfsk import RFM9xFSK  # type: ignore

# Type hinting only
try:
    from busio import SPI
    from digitalio import DigitalInOut

    from lib.adafruit_rfm.rfm_common import RFMSPI
except ImportError:
    pass


class RFM9xFactory:
    """Factory class for creating RFM9x radio instances.
    The purpose of the factory class is to hide the complexity of radio initialization from the caller.
    Specifically we should try to keep adafruit_rfm to only this factory class with the exception of the RFMSPI class.
    """

    @classmethod
    @with_retries(max_attempts=3, initial_delay=1)
    def create(
        cls,
        logger: Logger,
        modulation: RFM9xModulation,
        spi: SPI,
        chip_select: DigitalInOut,
        reset: DigitalInOut,
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
        :param RFM9xModulation modulation: Either FSK or LoRa.
        :param int sender_id: ID of the sender radio.
        :param int receiver_id: ID of the receiver radio.
        :param int frequency: Frequency at which the radio will transmit.
        :param int transmit_power: Transmit power level (applicable for LoRa only).
        :param int lora_spreading_factor: Spreading factor for LoRa modulation (applicable for LoRa only).

        :raises HardwareInitializationError: If the radio fails to initialize.

        :return An instance of the RFMSPI class, either RFM9xFSK or RFM9x based on the mode.
        """
        logger.debug(message="Initializing radio", modulation=modulation)

        try:
            if modulation == RFM9xModulation.FSK:
                radio: RFMSPI = cls.create_fsk_radio(
                    spi,
                    chip_select,
                    reset,
                    frequency,
                )
            else:
                radio: RFMSPI = cls.create_lora_radio(
                    spi,
                    chip_select,
                    reset,
                    frequency,
                    transmit_power,
                    lora_spreading_factor,
                )

            radio.node = sender_id
            radio.destination = receiver_id

            return radio
        except Exception as e:
            raise HardwareInitializationError(
                "Failed to initialize radio with modulation {modulation}"
            ) from e

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

    @staticmethod
    def get_instance_modulation(radio: RFMSPI) -> RFM9xModulation:
        """Determine the radio modulation in use.

        :param RFMSPI radio: The radio instance to check.

        :return The modulation in use.
        """
        if isinstance(radio, RFM9xFSK):
            return RFM9xModulation.FSK

        return RFM9xModulation.LORA
