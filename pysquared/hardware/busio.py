from busio import SPI
from microcontroller import Pin

from ..logger import Logger
from .decorators import with_retries
from .exception import HardwareInitializationError

try:
    from typing import Optional
except ImportError:
    pass


@with_retries(max_attempts=3, initial_delay=1)
def initialize_spi_bus(
    logger: Logger,
    clock: Pin,
    mosi: Optional[Pin] = None,
    miso: Optional[Pin] = None,
    baudrate: Optional[int] = 100000,
    phase: Optional[int] = 0,
    polarity: Optional[int] = 0,
    bits: Optional[int] = 8,
) -> SPI:
    """Initializes a SPI bus"

    :param Logger logger: The logger instance to log messages.
    :param Pin clock: The pin to use for the clock signal.
    :param Pin mosi: The pin to use for the MOSI signal.
    :param Pin miso: The pin to use for the MISO signal.
    :param int baudrate: The baudrate of the SPI bus (default is 100000).
    :param int phase: The phase of the SPI bus (default is 0).
    :param int polarity: The polarity of the SPI bus (default is 0).
    :param int bits: The number of bits per transfer (default is 8).

    :raises HardwareInitializationError: If the SPI bus fails to initialize.

    :return ~busio.SPI: The initialized SPI object.
    """
    logger.debug("Initializing spi")

    try:
        spi = SPI(clock, mosi, miso)
        spi.try_lock()
        spi.configure(baudrate, phase, polarity, bits)
        spi.unlock()
        return spi
    except Exception as e:
        raise HardwareInitializationError("Failed to initialize spi") from e
