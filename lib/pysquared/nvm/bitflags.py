try:
    from stubs.circuitpython.byte_array import ByteArray
except ImportError:
    pass


class bitFlag:
    """
    get() -> bool: Check if specific bit in a specific byte (held in byte array of nvm) is on (1 -> True) or off (0 -> False)
    toggle(value: bool) -> None: Set specific bit in a specific byte (held in byte array of nvm) to on (1) or off (0)
    """

    def __init__(self, index: int, bit: int, datastore: ByteArray) -> None:
        self._index = index  # Index of specific byte in array of bytes
        self._bit = bit  # Position of bit within specific byte
        self._datastore = datastore  # Array of bytes (Non-volatile Memory)
        self._bit_mask = 1 << (bit % 8)  # Creating bitmask with bit position
        # Ex. bit = 3 -> 3 % 8 = 3 -> 1 << 3 = 00001000

    def get(self) -> bool:  # Return if bit value/flag is on (1) or off (0)
        return bool(self._datastore[self._index] & self._bit_mask)

    def toggle(self, value: bool) -> None:
        if value:
            # If true, perform OR on specific byte and bitmask to set bit to set specific bit to 1
            self._datastore[self._index] |= self._bit_mask
        else:
            # If false, perform AND on specific byte and inverted bitmask to set specific bit to 0
            self._datastore[self._index] &= ~self._bit_mask
