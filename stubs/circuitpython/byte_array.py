"""
Stub for Circuit Python ByteArray class
https://docs.circuitpython.org/en/stable/shared-bindings/nvm/index.html#nvm.ByteArray

This stub has been contributed to the Adafruit CircuitPython Typing repo and can be removed after it has been approved and merged:
https://github.com/adafruit/Adafruit_CircuitPython_Typing/pull/46
"""

from typing import Union, overload

from circuitpython_typing import ReadableBuffer
from typing_extensions import Protocol


class ByteArray(Protocol):
    """
    Presents a stretch of non-volatile memory as a bytearray.

    Non-volatile memory is available as a byte array that persists over reloads and power cycles. Each assignment causes an erase and write cycle so its recommended to assign all values to change at once.
    """

    def __bool__(self) -> bool: ...

    def __len__(self) -> int:
        """Return the length. This is used by (len)"""

    @overload
    def __getitem__(self, index: slice) -> bytearray: ...

    @overload
    def __getitem__(self, index: int) -> int: ...

    def __getitem__(self, index: Union[slice, int]) -> Union[bytearray, int]:
        """Returns the value at the given index."""

    @overload
    def __setitem__(self, index: slice, value: ReadableBuffer) -> None: ...

    @overload
    def __setitem__(self, index: int, value: int) -> None: ...

    def __setitem__(
        self, index: Union[slice, int], value: Union[ReadableBuffer, int]
    ) -> None:
        """Set the value at the given index."""
