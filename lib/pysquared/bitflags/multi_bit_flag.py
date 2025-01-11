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

    _register_reader: Callable[[Any, int], int]
    _register_writer: Callable[[Any, int, int], None]

    def __init__(
        self, num_bits, register, lowest_bit, register_reader, register_writer
    ):
        self._register_reader = register_reader
        self._register_writer = register_writer

        self.maxval = (1 << num_bits) - 1
        self.bit_mask = self.maxval << lowest_bit
        self.lowest_bit = lowest_bit
        self.byte = register

    def __get__(self, obj, objtype=None):
        return (
            self._register_reader(obj, self.byte) & self.bit_mask
        ) >> self.lowest_bit

    def __set__(self, obj, value):
        if value >= self.maxval:
            value = self.maxval
        value <<= self.lowest_bit
        reg = self._register_reader(obj, self.byte)
        reg &= ~self.bit_mask
        self._register_writer(obj, self.byte, reg | value)


def rp2040_register_reader(obj: Any, register: int) -> int:
    """
    Hardware abstraction for interacting with registers on the RP2040
    """
    return obj.micro.nvm[register]


def rp2040_register_writer(obj: Any, register: int, value: int) -> None:
    """
    Hardware abstraction for interacting with registers on the RP2040
    """
    obj.micro.nvm[register] = value
