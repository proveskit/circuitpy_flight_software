from collections import defaultdict
from typing import Any, Callable, Tuple

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


def test_writing_to_multiple_registers():
    class MultiBitFlagTester:
        mock_register_reader, mock_register_writer = mock_register()

        mbf1 = multi_bit_flag.multiBitFlag(
            8, 0, 0, mock_register_reader, mock_register_writer
        )

        mbf2 = multi_bit_flag.multiBitFlag(
            8, 1, 0, mock_register_reader, mock_register_writer
        )

    c = MultiBitFlagTester()
    c.mbf1 = 1
    c.mbf2 = 2
    assert c.mbf1 == 1
    assert c.mbf2 == 2


def test_lowest_bit_low():
    lowest_bit = 0

    class MultiBitFlagTester:
        mock_register_reader, mock_register_writer = mock_register()

        mbf = multi_bit_flag.multiBitFlag(
            8, 0, lowest_bit, mock_register_reader, mock_register_writer
        )

    c = MultiBitFlagTester()
    assert c.mbf == 0


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


def test_arithmatic():
    class MultiBitFlagTester:
        mock_register_reader, mock_register_writer = mock_register()

        mbf = multi_bit_flag.multiBitFlag(
            8, 0, 0, mock_register_reader, mock_register_writer
        )

    c = MultiBitFlagTester()
    c.mbf += 1
    assert c.mbf == 1
    c.mbf += 999
    assert c.mbf == 255
    c.mbf -= 1
    assert c.mbf == 254


def test_negative_behavior():
    class MultiBitFlagTester:
        mock_register_reader, mock_register_writer = mock_register()

        mbf = multi_bit_flag.multiBitFlag(
            8, 0, 0, mock_register_reader, mock_register_writer
        )

    c = MultiBitFlagTester()

    c.mbf = -1
    assert c.mbf == 255

    c.mbf -= 300
    assert c.mbf == 211


def test_four_bit_length():
    class MultiBitFlagTester:
        mock_register_reader, mock_register_writer = mock_register()

        mbf = multi_bit_flag.multiBitFlag(
            4, 0, 0, mock_register_reader, mock_register_writer
        )

    c = MultiBitFlagTester()

    c.mbf = 0
    assert c.mbf == 0

    c.mbf = 16
    assert c.mbf == 15
