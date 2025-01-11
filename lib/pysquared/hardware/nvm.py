"""
Hardware abstraction for the CircuitPython non-volatile memory API
https://docs.circuitpython.org/en/stable/shared-bindings/nvm/index.html
"""

import microcontroller


def reader(index: int | slice) -> int | bytearray:
    """
    reader reads from the non-volatile memory
    """
    return microcontroller.nvm[index]


def writer(index: int | slice, value: int) -> None:
    """
    writer writes to the non-volatile memory
    """
    microcontroller.nvm[index] = value
