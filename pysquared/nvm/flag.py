try:
    from stubs.circuitpython.byte_array import ByteArray
except ImportError:
    pass


class Flag:
    """
    Flag class for managing boolean flags stored in non-volatile memory
    """

    def __init__(self, index: int, bit_index: int, datastore: ByteArray) -> None:
        self._index = index  # Index of specific byte in array of bytes
        self._bit = bit_index  # Position of bit within specific byte
        self._datastore = datastore  # Array of bytes (Non-volatile Memory)
        self._bit_mask = 1 << bit_index  # Creating bitmask with bit position
        # Ex. bit = 3 -> 3 % 8 = 3 -> 1 << 3 = 00001000

    def get(self) -> bool:
        """Get flag value"""
        return bool(self._datastore[self._index] & self._bit_mask)

    def toggle(self, value: bool) -> None:
        """Toggle flag value"""
        if value:
            # If true, perform OR on specific byte and bitmask to set bit to 1
            self._datastore[self._index] |= self._bit_mask
        else:
            # If false, perform AND on specific byte and inverted bitmask to set bit to 0
            self._datastore[self._index] &= ~self._bit_mask
