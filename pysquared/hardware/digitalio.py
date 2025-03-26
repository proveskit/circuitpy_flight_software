from digitalio import DigitalInOut, Direction
from microcontroller import Pin

from pysquared.hardware.decorators import with_retries
from pysquared.hardware.exception import HardwareInitializationError
from pysquared.logger import Logger


@with_retries(max_attempts=3, initial_delay=1)
def initialize_pin(
    logger: Logger, pin: Pin, direction: Direction, initial_value: bool
) -> DigitalInOut:
    """Initializes a DigitalInOut pin.

    :param Logger logger: The logger instance to log messages.
    :param Pin pin: The pin to initialize.
    :param Direction direction: The direction of the pin.
    :param bool initial_value: The initial value of the pin (default is True).

    :raises HardwareInitializationError: If the pin fails to initialize.

    :return ~digitalio.DigitalInOut: The initialized DigitalInOut object.
    """
    logger.debug(
        message="Initializing pin",
        initial_value=initial_value,
    )

    try:
        digital_in_out = DigitalInOut(pin)
        digital_in_out.direction = direction
        digital_in_out.value = initial_value
        return digital_in_out
    except Exception as e:
        raise HardwareInitializationError("Failed to initialize pin") from e
