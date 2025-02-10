"""
Stub for Circuit Python busio
https://docs.circuitpython.org/en/latest/shared-bindings/microcontroller/index.html
"""

from __future__ import annotations

import sys
from typing import Optional

from circuitpython_typing import ReadableBuffer, WriteableBuffer
from typing_extensions import Protocol

import stubs.circuitpython.microcontroller as microcontroller


class SPI(Protocol):
    def __init__(
        self,
        clock: microcontroller.Pin,
        MOSI: Optional[microcontroller.Pin] = None,
        MISO: Optional[microcontroller.Pin] = None,
        half_duplex: bool = False,
    ) -> None: ...

    def deinit(self) -> None: ...

    def __enter__(self) -> SPI: ...

    def __exit__(self) -> None: ...

    def configure(
        self,
        *,
        baudrate: int = 100000,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
    ) -> None: ...

    def try_lock(self) -> bool: ...

    def unlock(self) -> None: ...

    def write(
        self, buffer: ReadableBuffer, *, start: int = 0, end: int = sys.maxsize
    ) -> None: ...

    def readinto(
        self,
        buffer: WriteableBuffer,
        *,
        start: int = 0,
        end: int = sys.maxsize,
        write_value: int = 0,
    ) -> None: ...

    def write_readinto(
        self,
        out_buffer: ReadableBuffer,
        in_buffer: WriteableBuffer,
        *,
        out_start: int = 0,
        out_end: int = sys.maxsize,
        in_start: int = 0,
        in_end: int = sys.maxsize,
    ) -> None: ...

    frequency: int
