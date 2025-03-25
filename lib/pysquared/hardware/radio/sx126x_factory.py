from lib.proves_sx126.sx1262 import SX1262
from lib.pysquared.config.radio import RadioConfig
from lib.pysquared.hardware.decorators import with_retries
from lib.pysquared.hardware.exception import HardwareInitializationError
from lib.pysquared.hardware.radio.modulation import RadioModulation
from lib.pysquared.logger import Logger

# Type hinting only
try:
    from busio import SPI
    from digitalio import DigitalInOut

    from lib.sx126.sx1262 import SX1262
except ImportError:
    pass


class SX126xFactory:
    """Factory class for creating RFM9x radio instances.
    The purpose of the factory class is to hide the complexity of radio initialization from the caller.
    Specifically we should try to keep adafruit_rfm to only this factory class with the exception of the RFMSPI class.
    """

    def __init__(
        self,
        spi: SPI,
        chip_select: DigitalInOut,
        irq: DigitalInOut,
        reset: DigitalInOut,
        gpio: DigitalInOut,
        radio_config: RadioConfig,
        tx_enable: DigitalInOut,
        rx_enable: DigitalInOut,
    ) -> None:
        """Initialize the factory class.

        :param busio.SPI spi: The SPI bus connected to the chip. Ensure SCK, MOSI, and MISO are connected.
        :param ~digitalio.DigitalInOut cs: A DigitalInOut object connected to the chip's CS/chip select line.
        :param ~digitalio.DigitalInOut reset: A DigitalInOut object connected to the chip's RST/reset line.
        :param RadioConfig radio_config: Radio config object.
        """
        self._spi = spi
        self._chip_select = chip_select
        self._irq = irq
        self._reset = reset
        self._gpio = gpio
        self._radio_config = radio_config
        self.tx_enable = tx_enable
        self.rx_enable = rx_enable

    @with_retries(max_attempts=1, initial_delay=1)
    def create(
        self,
        logger: Logger,
        modulation: RadioModulation = RadioModulation.LORA,
    ) -> SX1262:
        """Create a RFM9x radio instance.

        :param Logger logger: Logger instance for logging messages.
        :param RFM9xModulation modulation: Either FSK or LoRa.

        :raises HardwareInitializationError: If the radio fails to initialize.

        :return An instance of the RFMSPI class, either RFM9xFSK or RFM9x based on the mode.
        """
        logger.debug(message="Initializing radio", modulation=modulation)

        try:
            radio: SX1262 = SX1262(
                self._spi, self._chip_select, self._irq, self._reset, self._gpio
            )

            if modulation == RadioModulation.FSK:
                radio.beginFSK(
                    freq=self._radio_config.transmit_frequency,
                    addr=self._radio_config.fsk.broadcast_address,
                )
            else:
                radio.begin(
                    freq=self._radio_config.transmit_frequency,
                    cr=self._radio_config.lora.coding_rate,
                    crcOn=self._radio_config.lora.cyclic_redundancy_check,
                    sf=self._radio_config.lora.spreading_factor,
                    power=self._radio_config.lora.transmit_power,
                )

            return radio
        except Exception as e:
            raise HardwareInitializationError(
                f"Failed to initialize radio with modulation {modulation}"
            ) from e

    @staticmethod
    def get_instance_modulation(radio: SX1262) -> RadioModulation:
        """Determine the radio modulation in use.

        :param RFMSPI radio: The radio instance to check.

        :return The modulation in use.
        """
        return radio.radio_modulation
