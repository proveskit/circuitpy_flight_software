class bitFlag:
    """
    Single bit register WITHIN a byte that can be read or set
    values are 'bool'

    Assumes register is read MSB!

    """

    def __init__(self, register, bit):
        self.bit_mask = 1 << (bit % 8)  # the bitmask *within* the byte!
        self.byte = register

    def __get__(self, obj, objtype=None):
        return bool(obj.micro.nvm[self.byte] & self.bit_mask)

    def __set__(self, obj, value):
        if value:
            obj.micro.nvm[self.byte] |= self.bit_mask
        else:
            obj.micro.nvm[self.byte] &= ~self.bit_mask


class multiByte:
    """
    must be whole bytes
    MSB
    """

    def __init__(self, num_bytes, lowest_register):
        self.maxval = (1 << (8 * num_bytes)) - 1
        self.start = lowest_register
        self.stop = lowest_register + num_bytes
        self.num_bytes = num_bytes

    def __get__(self, obj, objtype=None):
        return int.from_bytes(obj.micro.nvm[self.start : self.stop], "big")

    def __set__(self, obj, value):
        if value >= self.maxval:
            value = self.maxval
        obj.micro.nvm[self.start : self.stop] = value.to_bytes(self.num_bytes, "big")
