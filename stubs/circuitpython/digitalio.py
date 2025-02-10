"""
Stub for Circuit Python digitalio
https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/index.html
"""

from __future__ import annotations

from typing import Optional

import stubs.circuitpython.microcontroller as microcontroller
from typing_extensions import Protocol


class DriveMode(Protocol):
    PUSH_PULL: 'DriveMode'
    OPEN_DRAIN: 'DriveMode'
    
    def __init__(self) -> None: ...

class DigitalInOut(Protocol):
    def __init__(self, pin: microcontroller.Pin) -> None: ...
    
    def deinit(self) -> None: ...
    
    def __enter__(self) -> DigitalInOut: ...
    
    def __exit__(self) -> None: ...
    
    def switch_to_output(self, value: bool = False, drive_mode: DriveMode = DriveMode.PUSH_PULL) -> None: ...
    
    def switch_to_input(self, pull: Optional[Pull] = None) -> None: ...
        
    direction: Direction
    value: bool
    drive_mode: DriveMode
    pull: Optional[Pull]


class Direction(Protocol):
    def __init__(self) -> None: ...
    INPUT: Direction
    OUTPUT: Direction

class Pull(Protocol):
    def __init__(self) -> None: ...
    UP: Pull
    DOWN: Pull
