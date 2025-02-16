"""
Mock for Circuit Python digitalio
https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/index.html
"""

from __future__ import annotations

import mocks.circuitpython.microcontroller as microcontroller


class DriveMode:
    pass


class DigitalInOut:
    def __init__(self, pin: microcontroller.Pin) -> None: ...


class Direction:
    pass


class Pull:
    pass
