"""
Mock for Circuit Python microcontroller
https://docs.circuitpython.org/en/latest/shared-bindings/busio/index.html
"""

from typing_extensions import Protocol


class Pin(Protocol):
    def __init__(self) -> None: ...

    def __hash__(self) -> int: ...
