"""
Mock for Circuit Python busio
https://docs.circuitpython.org/en/latest/shared-bindings/microcontroller/index.html
"""

from __future__ import annotations

from typing import Optional

import mocks.circuitpython.microcontroller as microcontroller


class SPI:
    def __init__(
        self,
        clock: microcontroller.Pin,
        MOSI: Optional[microcontroller.Pin] = None,
        MISO: Optional[microcontroller.Pin] = None,
        half_duplex: bool = False,
    ) -> None: ...
