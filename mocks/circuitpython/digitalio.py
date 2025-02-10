from __future__ import annotations

from typing import Optional

import stubs.circuitpython.microcontroller as microcontroller
from stubs.circuitpython.digitalio import DigitalInOut as DigitalInOutStub


class DriveMode:
    def __init__(self) -> None: ...

    PUSH_PULL: DriveMode = None
    OPEN_DRAIN: DriveMode = None


class DigitalInOut(DigitalInOutStub):
    def __init__(self, pin: microcontroller.Pin) -> None:
        pass

    def deinit(self) -> None:
        pass

    def __enter__(self) -> DigitalInOut:
        pass

    def __exit__(self) -> None:
        pass

    def switch_to_output(
        self, value: bool = False, drive_mode: DriveMode = DriveMode.PUSH_PULL
    ) -> None:
        pass

    def switch_to_input(self, pull: Optional[Pull] = None) -> None:
        pass

    direction: Direction
    value: bool
    drive_mode: DriveMode
    pull: Optional[Pull]


class Direction:
    def __init__(self) -> None: ...

    INPUT: Direction
    OUTPUT: Direction


class Pull:
    def __init__(self) -> None: ...

    UP: Pull
    DOWN: Pull
