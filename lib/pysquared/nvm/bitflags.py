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
