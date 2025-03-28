from ....logger import Logger
from ...decorators import with_retries
from ...exception import HardwareInitializationError
from ..magnetometer_factory_protocol import MagnetometerFactoryProto

try:
    from mocks.circuitpython.adafruit_lis2mdl.lis2mdl import LIS2MDL  # type: ignore
except ImportError:
    from lib.adafruit_lis2mdl import LIS2MDL

# Type hinting only
try:
    from busio import I2C
except ImportError:
    pass


class LIS2MDLFactory(MagnetometerFactoryProto):
    """Factory class for creating LIS2MDL magnetometer instances.
    The purpose of the factory class is to hide the complexity of magnetometer initialization from the caller.
    Specifically we should try to keep adafruit_lis2mdl to only this factory class.
    """

    _instance: LIS2MDL | None = None

    def __init__(
        self,
        logger: Logger,
        i2c: I2C,
    ) -> None:
        """Initialize the factory class.

        :param Logger logger: Logger instance for logging messages.
        :param busio.I2C i2c: The I2C bus connected to the chip.
        """
        self._log: Logger = logger
        self._i2c: I2C = i2c

    @with_retries(max_attempts=3, initial_delay=1)
    @property
    def _magnetometer(self) -> LIS2MDL:
        """Create the magnetometer instance if it does not exist.

        :return: The LIS2MDL instance.
        :raises HardwareInitializationError: If the magnetometer fails to initialize.
        """
        if self._instance is None:
            try:
                self._log.debug("Initializing magnetometer")
                self._instance = LIS2MDL(self._i2c)
            except Exception as e:
                raise HardwareInitializationError(
                    "Failed to initialize magnetometer"
                ) from e
        return self._instance

    def get_vector(self) -> tuple[float, float, float]:
        """Get the magnetic field vector from the magnetometer.

        :return: A tuple containing the x, y, and z magnetic field values in Gauss.
        :raises Exception: If there is an error retrieving the values.
        """
        try:
            return self._magnetometer.magnetic
        except Exception as e:
            self._log.error(
                "There was an error retrieving the magnetometer sensor values", e
            )
