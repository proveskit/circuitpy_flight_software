import pytest

import lib.pysquared.nvm.bitflags as bitflags
from mocks.circuitpython.byte_array import ByteArray


@pytest.fixture
def setup_datastore():
    return ByteArray(size=17)


def test_init(setup_datastore):
    flag = bitflags.bitFlag(16, 0, setup_datastore)  # Example flag for softboot
    assert flag._index == 16  # Check if _index (index of byte array) is set to 16
    assert flag._bit == 0  # Check if _bit (bit position) is set to first index of byte
    assert flag._bit_mask == 0b00000001  # Check if _bit_mask is set correctly


def test_get(setup_datastore):
    flag = bitflags.bitFlag(16, 1, setup_datastore)  # Example flag for solar
    assert setup_datastore[16] == 0b00000000
    assert flag.get().equals(False)  # Bit should be 0 by default

    setup_datastore[16] = 0b00000010  # Manually set bit to test
    assert flag.get().equals(True)  # Should return true since bit position 1 = 1


def test_toggle(setup_datastore):
    flag = bitflags.bitFlag(16, 2, setup_datastore)  # Example flag for burnarm
    assert setup_datastore[16] == 0b00000000
    flag.toggle(False)  # Set flag to off (bit to 0)
    assert setup_datastore[16] == 0b00000000
    assert flag.get().equals(False)  # Bit should remain 0 due to 0 by default

    flag.toggle(True)  # Set flag to on (bit to 1)
    assert setup_datastore[16] == 0b00000100  # Check if bit position 2 = 1
    assert flag.get().equals(True)  # Bit should be flipped to 1

    flag.toggle(True)  # Set flag to on (bit to 1)
    assert setup_datastore[16] == 0b00000100  # Check if bit position 2 = 1
    assert flag.get().equals(True)  # Bit should remain 1 due to already being set to on

    flag.toggle(False)  # Set flag back to off (bit to 0)
    assert setup_datastore[16] == 0b00000000  # Check if bit position 2 = 0
    assert flag.get().equals(False)  # Bit should be 0


def test_edge_cases(setup_datastore):
    first_bit = bitflags.bitFlag(0, 0, setup_datastore)
    first_bit.toggle(True)
    assert setup_datastore[0] == 0b00000001
    assert first_bit.get().equals(True)

    last_bit = bitflags.bitFlag(0, 7, setup_datastore)
    last_bit.toggle(True)
    assert setup_datastore[0] == 0b10000001
    assert last_bit.get().equals(True)
