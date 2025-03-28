from ...logger import Logger
from ..decorators import with_retries
from ..exception import HardwareInitializationError

try:
    from lib.adafruit_lis2mdl import LIS2MDL
except ImportError:
    pass
    # from mocks.circuitpython.adafruit_rfm.rfm9x import RFM9x  # type: ignore
    # from mocks.circuitpython.adafruit_rfm.rfm9xfsk import RFM9xFSK  # type: ignore

# Type hinting only
try:
    from busio import I2C
except ImportError:
    pass


class LIS2MDLFactory:
    """Factory class for creating LIS2MDL magnetometer instances.
    The purpose of the factory class is to hide the complexity of magnetometer initialization from the caller.
    Specifically we should try to keep adafruit_lis2mdl to only this factory class.
    """

    def __init__(
        self,
        i2c: I2C,
    ) -> None:
        """Initialize the factory class.

        :param busio.I2C i2c: The I2C bus connected to the chip.
        """
        self._i2c: I2C = i2c

    @with_retries(max_attempts=3, initial_delay=1)
    def create(
        self,
        logger: Logger,
    ) -> LIS2MDL:
        """Create an LIS2MDL magnetometer instance.

        :param Logger logger: Logger instance for logging messages.

        :raises HardwareInitializationError: If the magnetometer fails to initialize.

        :return: An instance of the LIS2MDL class.
        """
        logger.debug("Initializing magnetometer")

        try:
            return LIS2MDL(self._i2c)
        except Exception as e:
            raise HardwareInitializationError(
                "Failed to initialize magnetometer"
            ) from e
