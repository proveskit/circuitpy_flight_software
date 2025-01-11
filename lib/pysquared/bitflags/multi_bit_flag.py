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
        bit_length: int,
        index: int,
        nvm_reader: Callable[[Any, int], int],
        nvm_writer: Callable[[Any, int, int], None],
    ):
        self._nvm_reader = nvm_reader
        self._nvm_writer = nvm_writer

        self.maxval = (1 << bit_length) - 1
        self.bit_mask = self.maxval
        self.byte = index

    def __get__(self, obj, objtype=None):
        return self._nvm_reader(self.byte) & self.bit_mask

    def __set__(self, obj, value):
        if value >= self.maxval:
            value = self.maxval
        reg = self._nvm_reader(self.byte)
        reg &= ~self.bit_mask
        self._nvm_writer(self.byte, reg | value)
