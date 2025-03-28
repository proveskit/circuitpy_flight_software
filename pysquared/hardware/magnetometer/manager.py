# # Type hinting only
# try:
#     from typing import Union

#     from pysquared.hardware.magnetometer.magnetometer_factory_protocol import MagnetometerFactoryProto
#     from pysquared.logger import Logger
# except ImportError:
#     pass


# class MagnetometerManager:
#     """Manages the lifecycle of the magnetometer."""

#     _magnetometer: MagnetometerFactoryProto | None = None

#     def __init__(
#         self,
#         logger: Logger,
#         magnetometer_factory: MagnetometerFactoryProto,
#     ) -> None:
#         """Initialize the magnetometer manager.

#         :param Logger logger: Logger instance for logging messages.
#         :param MagnetometerFactory magnetometer_factory: Factory for creating hardware specific magnetometer instances.

#         :raises HardwareInitializationError: If the magnetometer fails to initialize.
#         """
#         self._log = logger
#         self._magnetometer_factory = magnetometer_factory

#         self._magnetometer = self.magnetometer

#     @property
#     def magnetometer(self) -> MagnetometerFactoryProto:
#         """Get the current magnetometer instance, creating it if needed.
#         :return MagnetometerFactoryProto: The magnetometer instance.
#         """
#         if self._magnetometer is None:
#             self._magnetometer = self._magnetometer_factory.create()

#         return self._magnetometer

#     def get_vector(self) -> Union[tuple[float, float, float], None]:
#         """Get the magnetic field vector from the magnetometer.

#         :return: A tuple containing the x, y, and z magnetic field values in Gauss.
#         :raises Exception: If there is an error retrieving the values."
#         """
#         try:
#             return self.mangetometer.magnetic
#         except Exception as e:
#             self._log.error(
#                 "There was an error retrieving the magnetometer sensor values", e
#             )
