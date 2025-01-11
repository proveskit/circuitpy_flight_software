try:
    from typing import Any, Callable
except ImportError:
    pass


class multiBitFlag:
    """
    Multi-bit value WITHIN a byte that can be read or set
    values are int

    Assumes register is read MSB!
        0x80 = 0b10000000
            bit#:76543210
    """

    def __init__(
        self,
        index: int,
        bit_length: int,
        nvm_reader: Callable[[Any, int], int],
        nvm_writer: Callable[[Any, int, int], None],
    ):
        self._index = index
        self._nvm_reader = nvm_reader
        self._nvm_writer = nvm_writer

        self._maxval = (1 << bit_length) - 1
        self._bit_mask = self._maxval

    def __get__(self, obj, objtype=None):
        return self._nvm_reader(self._index) & self._bit_mask

    def __set__(self, obj, value):
        reg = self._nvm_reader(self._index)
        reg &= ~self._bit_mask
        value = min(reg | value, self._maxval)
        self._nvm_writer(self._index, reg | value)
