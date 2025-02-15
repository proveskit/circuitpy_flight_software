from lib.pysquared.hardware.rfm9x.modulation import RFM9xModulation

# Type hinting only
try:
    from busio import SPI
    from digitalio import DigitalInOut

    from lib.adafruit_rfm.rfm_common import RFMSPI
    from lib.pysquared.hardware.rfm9x.factory import RFM9xFactory
    from lib.pysquared.logger import Logger
    from lib.pysquared.nvm.flag import Flag
except ImportError:
    pass


class RFM9xManager:
    """Manages the lifecycle and mode switching of the RFM9x radio."""

    _radio: RFMSPI | None = None

    def __init__(
        self,
        logger: Logger,
        use_fsk: Flag,
        radio_factory: RFM9xFactory,
        spi: SPI,
        chip_select: DigitalInOut,
        reset: DigitalInOut,
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
        self._log = logger
        self._use_fsk = use_fsk
        self._radio_factory = radio_factory
        self._spi = spi
        self._chip_select = chip_select
        self._reset = reset
        self._sender_id = sender_id
        self._receiver_id = receiver_id
        self._frequency = frequency
        self._transmit_power = transmit_power
        self._lora_spreading_factor = lora_spreading_factor

        self._radio = self.radio

    @property
    def radio(self) -> RFMSPI:
        """Get the current radio instance, creating it if needed.
        :return ~lib.adafruit_rfm.rfm_common.RFMSPI: The RFM9x radio instance.
        """
        if self._radio is None:
            self._radio = self._radio_factory.create(
                self._log,
                self.get_modulation(),
                self._spi,
                self._chip_select,
                self._reset,
                self._sender_id,
                self._receiver_id,
                self._frequency,
                self._transmit_power,
                self._lora_spreading_factor,
            )

            # TODO: We should use some default modulation value set in the config file
            # instead of always toggling back to LoRa
            self.set_modulation(RFM9xModulation.LORA)

        return self._radio

    def get_modulation(self) -> str:
        """Get the current radio modulation.
        :return str: The current radio modulation.
        """
        if self._radio is None:
            return RFM9xModulation.FSK if self._use_fsk.get() else RFM9xModulation.LORA

        return self._radio_factory.get_instance_modulation(self._radio)

    def set_modulation(self, req_modulation: RFM9xModulation) -> None:
        """
        Set the radio modulation.
        Takes effect on the next reboot.
        :param lib.radio.RFM9xModulation req_modulation: The modulation to switch to.
        :return: None
        """
        if self.get_modulation() != req_modulation:
            self._use_fsk.toggle(req_modulation == RFM9xModulation.FSK)
            self._log.info(
                "Radio modulation change requested", modulation=req_modulation
            )

    def get_temperature(self) -> int:
        """Get the temperature from the radio.
        :return int: The temperature in degrees Celsius.
        """
        raw_temp = self.radio.read_u8(0x5B)
        temp = raw_temp & 0x7F
        if (raw_temp & 0x80) == 0x80:
            temp = ~temp + 0x01

        prescaler = 143
        return temp + prescaler
