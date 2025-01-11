from collections import defaultdict
from typing import Any, Callable, Tuple

import pytest

import lib.pysquared.bitflags.multi_bit_flag as multi_bit_flag


def mock_register() -> (
    Tuple[Callable[[Any, int], int], Callable[[Any, int, int], None]]
):
    data = defaultdict(int)

    def reader(obj: Any, register: int) -> int:
        return data[register]

    def writer(obj: Any, register: int, value: int):
        data[register] = value

    return reader, writer


@pytest.mark.parametrize(
    "bit_length, register_idx, lowest_bit, initial_value, expected_value",
    [
        (8, 0, 0, 0, 0),  # minimum 8 bit value
        (8, 0, 0, 255, 255),  # maximum 8 bit value
        (8, 0, 0, 999, 255),  # value greater than 8 bits
        (8, 0, 0, -1, 255),  # negative value
        (8, 0, 0, -300, 212),  # negative value
        (4, 0, 0, 0, 0),  # minimum 4 bit value
        (4, 0, 0, 16, 15),  # maximum 4 bit value
    ],
)
def test_multi_bit_flag(
    bit_length, register_idx, lowest_bit, initial_value, expected_value
):
    class MultiBitFlagTester:
        mock_register_reader, mock_register_writer = mock_register()

        mbf = multi_bit_flag.multiBitFlag(
            bit_length,
            register_idx,
            lowest_bit,
            mock_register_reader,
            mock_register_writer,
        )

    c = MultiBitFlagTester()
    c.mbf = initial_value
    assert c.mbf == expected_value


# Defining lowest bit isn't working?
# def test_lowest_bit_high():
#     lowest_bit = 255
#     class MultiBitFlagTester:
#         mock_register_reader, mock_register_writer = mock_register()
#         mbf = multi_bit_flag.multiBitFlag(
#             8, 0, lowest_bit, mock_register_reader, mock_register_writer
#         )
#     c = MultiBitFlagTester()
#     assert c.mbf == 255


def test_arithmetic():
    bit_length, register_idx, lowest_bit = 8, 0, 0

    class MultiBitFlagTester:
        mock_register_reader, mock_register_writer = mock_register()

        mbf = multi_bit_flag.multiBitFlag(
            bit_length,
            register_idx,
            lowest_bit,
            mock_register_reader,
            mock_register_writer,
        )

    c = MultiBitFlagTester()
    c.mbf = 1
    c.mbf += 2
    assert c.mbf == 3


def test_writing_to_multiple_registers():
    bit_length, register_idx, lowest_bit = 8, 0, 0
    register_idx2 = 1

    class MultiBitFlagTester:
        mock_register_reader, mock_register_writer = mock_register()

        mbf1 = multi_bit_flag.multiBitFlag(
            bit_length,
            register_idx,
            lowest_bit,
            mock_register_reader,
            mock_register_writer,
        )

        mbf2 = multi_bit_flag.multiBitFlag(
            bit_length,
            register_idx2,
            lowest_bit,
            mock_register_reader,
            mock_register_writer,
        )

    c = MultiBitFlagTester()
    c.mbf1 = 1
    c.mbf2 = 2
    assert c.mbf1 == 1
    assert c.mbf2 == 2
