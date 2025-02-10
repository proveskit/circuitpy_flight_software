"""
Stub for Circuit Python digitalio
https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/index.html
"""

from __future__ import annotations

from typing import Optional

from typing_extensions import Protocol

import stubs.circuitpython.microcontroller as microcontroller


class DriveMode(Protocol):
    def __init__(self) -> None: ...

    PUSH_PULL: DriveMode = None
    OPEN_DRAIN: DriveMode = None


class DigitalInOut(Protocol):
    def __init__(self, pin: microcontroller.Pin) -> None: ...

    def deinit(self) -> None: ...

    def __enter__(self) -> DigitalInOut: ...

    def __exit__(self) -> None: ...

    def switch_to_output(
        self, value: bool = False, drive_mode: DriveMode = DriveMode.PUSH_PULL
    ) -> None: ...

    def switch_to_input(self, pull: Optional[Pull] = None) -> None: ...

    direction: Direction = None
    value: bool = False
    drive_mode: DriveMode = None
    pull: Optional[Pull] = None


class Direction(Protocol):
    def __init__(self) -> None: ...

    INPUT: Direction = None
    OUTPUT: Direction = None


class Pull(Protocol):
    def __init__(self) -> None: ...

    UP: Pull = None
    DOWN: Pull = None
