try:
    from stubs.circuitpython.byte_array import ByteArray
except ImportError:
    pass


class Counter:
    def __init__(
        self,
        index: int,
        datastore: ByteArray,
    ) -> None:
        self._index = index
        self._datastore = datastore

    def get(self) -> int:
        """
        get returns the value of the counter
        """
        return self._datastore[self._index]

    def increment(self) -> None:
        """
        increment increases the counter by one
        """
        value: int = (self.get() + 1) & 0xFF  # 8-bit counter with rollover
        self._datastore[self._index] = value
