import sys
from typing import Optional

from circuitpython_typing import ReadableBuffer, WriteableBuffer

import stubs.circuitpython.microcontroller as microcontroller
from stubs.circuitpython.busio import SPI as SPIStub


class SPI(SPIStub):
    def __init__(
        self,
        clock: microcontroller.Pin,
        MOSI: Optional[microcontroller.Pin] = None,
        MISO: Optional[microcontroller.Pin] = None,
        half_duplex: bool = False,
    ) -> None:
        self.frequency = 0

    def deinit(self) -> None:
        pass

    def __enter__(self) -> "SPI":
        pass

    def __exit__(self) -> None:
        pass

    def configure(
        self,
        *,
        baudrate: int = 100000,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
    ) -> None:
        pass

    def try_lock(self) -> bool:
        return True

    def unlock(self) -> None:
        pass

    def write(
        self, buffer: ReadableBuffer, *, start: int = 0, end: int = sys.maxsize
    ) -> None:
        pass

    def readinto(
        self,
        buffer: WriteableBuffer,
        *,
        start: int = 0,
        end: int = sys.maxsize,
        write_value: int = 0,
    ) -> None:
        pass

    def write_readinto(
        self,
        out_buffer: ReadableBuffer,
        in_buffer: WriteableBuffer,
        *,
        out_start: int = 0,
        out_end: int = sys.maxsize,
        in_start: int = 0,
        in_end: int = sys.maxsize,
    ) -> None:
        pass
