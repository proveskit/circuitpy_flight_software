"""
This module defines a protocol for creating magnetometer instances.
This is useful for defining a factory interface that can be implemented by different classes
for different types of magnetometers. This allows for flexibility in the design of the system,
enabling the use of different magnetometer implementations without changing the code that uses them.

CircuitPython does not support Protocols directly, but this class can still be used to define a factory interface

https://docs.python.org/3/library/typing.html#typing.Protocol
"""

from lib.adafruit_lis2mdl import LIS2MDL


class MagnetometerFactoryProto:
    def create(self) -> LIS2MDL: ...

    def get_vector(self) -> tuple[float, float, float]: ...
