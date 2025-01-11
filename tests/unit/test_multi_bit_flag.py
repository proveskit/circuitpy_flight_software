from collections import defaultdict
from typing import Any

import lib.pysquared.bitflags.multi_bit_flag as multi_bit_flag

data = defaultdict(int)


def mock_register_reader(obj: Any, register):
    return data[register]


def mock_register_writer(obj: Any, register, value):
    data[register] = value


def test_set_get():
    mbf = multi_bit_flag.multiBitFlag(
        8, 0, 0, mock_register_reader, mock_register_writer
    )
    assert mbf.__get__(None) == 0
    mbf.__set__(None, 1)
    assert mbf.__get__(None) == 1
    mbf.__set__(None, 255)
    assert mbf.__get__(None) == 255
    mbf.__set__(None, 256)
    assert mbf.__get__(None) == 255
