from collections import defaultdict
from typing import Any, Callable, Tuple

import pytest

import lib.pysquared.bitflags.multi_bit_flag as multi_bit_flag


def mock_nvm() -> Tuple[Callable[[Any, int], int], Callable[[Any, int, int], None]]:
    data = defaultdict(int)

    def reader(index: int) -> int:
        return data[index]

    def writer(index: int, value: int) -> None:
        data[index] = value

    return reader, writer


@pytest.mark.parametrize(
    "bit_length, initial_value, expected_value",
    [
        (4, 0, 0),  # minimum 4 bit value
        (4, 15, 15),  # maximum 4 bit value
        (4, 999, 15),  # value greater than 4 bits
        (4, -4, 12),  # value less than 4 bits
        (8, 0, 0),  # minimum 8 bit value
        (8, 255, 255),  # maximum 8 bit value
        (8, 999, 255),  # value greater than 8 bits
        (8, -300, 212),  # value less than 8 bits
    ],
)
def test_multi_bit_flag_bounds(bit_length, initial_value, expected_value):
    """
    Test that the multiBitFlag class correctly handles values that are inside and outside the bounds of its bit length
    """
    index = 0

    class MultiBitFlagTester:
        mock_nvm_reader, mock_nvm_writer = mock_nvm()

        mbf = multi_bit_flag.multiBitFlag(
            index,
            bit_length,
            mock_nvm_reader,
            mock_nvm_writer,
        )

    c = MultiBitFlagTester()
    c.mbf = initial_value
    assert c.mbf == expected_value


def test_arithmetic():
    index, bit_length = 0, 8

    class MultiBitFlagTester:
        mock_nvm_reader, mock_nvm_writer = mock_nvm()

        mbf = multi_bit_flag.multiBitFlag(
            index,
            bit_length,
            mock_nvm_reader,
            mock_nvm_writer,
        )

    c = MultiBitFlagTester()
    c.mbf = 1
    c.mbf += 2
    assert c.mbf == 3


def test_writing_to_multiple_nvms():
    bit_length, index1, index2 = 8, 0, 1

    class MultiBitFlagTester:
        mock_nvm_reader, mock_nvm_writer = mock_nvm()

        mbf1 = multi_bit_flag.multiBitFlag(
            index1,
            bit_length,
            mock_nvm_reader,
            mock_nvm_writer,
        )

        mbf2 = multi_bit_flag.multiBitFlag(
            index2,
            bit_length,
            mock_nvm_reader,
            mock_nvm_writer,
        )

    c = MultiBitFlagTester()
    c.mbf1 = 1
    c.mbf2 = 2
    assert c.mbf1 == 1
    assert c.mbf2 == 2
