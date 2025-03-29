try:
    from mocks.circuitpython.adafruit_lsm6ds.lsm6dsox import LSM6DSOX  # type: ignore
except ImportError:
    from lib.adafruit_lsm6ds.lsm6dsox import LSM6DSOX

from ....logger import Logger
from ...decorators import with_retries
from ...exception import HardwareInitializationError
from ..imu_protocol import InertialMeasurementUnitProto

# Type hinting only
try:
    from busio import I2C
except ImportError:
    pass


class LSM6DSOXFactory(InertialMeasurementUnitProto):
    """Factory class for creating LIS2MDL magnetometer instances.
    The purpose of the factory class is to hide the complexity of magnetometer initialization from the caller.
    Specifically we should try to keep adafruit_lis2mdl to only this factory class.
    """

    @with_retries(max_attempts=3, initial_delay=1)
    def __init__(
        self,
        logger: Logger,
        i2c: I2C,
        address: int,
    ) -> None:
        """Initialize the factory class.

        :param Logger logger: Logger instance for logging messages.
        :param busio.I2C i2c: The I2C bus connected to the chip.

        :raises HardwareInitializationError: If the IMU fails to initialize.
        """
        self._log: Logger = logger

        try:
            self._log.debug("Initializing IMU")
            self._imu: LSM6DSOX = LSM6DSOX(i2c, address)
        except Exception as e:
            raise HardwareInitializationError("Failed to initialize IMU") from e

    def get_gyro_data(self) -> tuple[float, float, float] | None:
        """Get the gyroscope data from the inertial measurement unit.

        :return: A tuple containing the x, y, and z angular acceleration values in radians per second or None if not available.
        :rtype: tuple[float, float, float] | None

        :raises Exception: If there is an error retrieving the values.
        """
        try:
            return self._imu.gyro
        except Exception as e:
            self._log.error("Error retrieving IMU gyro sensor values", e)

    def get_acceleration(self) -> tuple[float, float, float] | None:
        """Get the acceleration data from the inertial measurement unit.

        :return: A tuple containing the x, y, and z acceleration values in m/s^2 or None if not available.
        :rtype: tuple[float, float, float] | None

        :raises Exception: If there is an error retrieving the values.
        """
        try:
            return self._imu.acceleration
        except Exception as e:
            self._log.error("Error retrieving IMU acceleration sensor values", e)

    def get_temperature(self) -> float | None:
        """Get the temperature reading from the inertial measurement unit, if available.

        :return: The temperature in degrees Celsius or None if not available.
        :rtype: float | None

        :raises Exception: If there is an error retrieving the temperature value.
        """
        try:
            return self._imu.temperature
        except Exception as e:
            self._log.error("Error retrieving IMU temperature sensor values", e)
