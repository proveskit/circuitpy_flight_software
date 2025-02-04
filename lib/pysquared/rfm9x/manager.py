import gc

from busio import SPI
from digitalio import DigitalInOut

from lib.adafruit_rfm.rfm_common import RFMSPI
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.flag import Flag
from lib.pysquared.rfm9x.factory import RFM9xFactory


class RFM9xManager:
    """Manages the lifecycle and mode switching of the RFM9x radio."""

    _radio: RFMSPI | None = None

    def __init__(
        self,
        logger: Logger,
        spi: SPI,
        chip_select: DigitalInOut,
        reset: DigitalInOut,
        use_fsk: Flag,
        sender_id: int,
        receiver_id: int,
        frequency: int,
        transmit_power: int,
        lora_spreading_factor: int,
    ):
        """Initialize the rfm9x manager.

        Stores configuration but doesn't create radio until needed.

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
        """
        self.logger = logger
        self.spi = spi
        self.chip_select = chip_select
        self.reset = reset
        self.use_fsk = use_fsk
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.frequency = frequency
        self.transmit_power = transmit_power
        self.lora_spreading_factor = lora_spreading_factor

        self._radio = self.radio

    @property
    def radio(self) -> RFMSPI:
        """Get the current radio instance, creating it if needed.
        :return ~lib.adafruit_rfm.rfm_common.RFMSPI: The RFM9x radio instance.
        """
        if self._radio is None:
            self.current_mode = RFM9xFactory.radio_mode(self.use_fsk)
            self._radio = RFM9xFactory.create(
                self.logger,
                self.spi,
                self.chip_select,
                self.reset,
                self.use_fsk,
                self.sender_id,
                self.receiver_id,
                self.frequency,
                self.transmit_power,
                self.lora_spreading_factor,
            )

            if self.use_fsk.get():
                self.logger.info("Next restart will be in LoRa mode.")
                self.use_fsk.toggle(False)

        return self._radio

    def switch_mode(self, use_fsk: bool) -> None:
        """
        Switch the radio between FSK and LoRa modes.
        :param bool use_fsk: True to switch to FSK mode, False for LoRa mode
        :return: None
        """
        self.use_fsk.toggle(use_fsk)

        if self.current_mode != RFM9xFactory.radio_mode(self.use_fsk):
            self.logger.info(
                "Radio mode change requested, deinitializing radio",
                requested_mode=RFM9xFactory.radio_mode(self.use_fsk),
            )
            self._radio = None
            gc.collect()
            self._radio = self.radio
