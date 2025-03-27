import time

import pytest

import mocks.circuitpython.rtc as MockRTC
from pysquared.rtc.rtc_common import RTC


@pytest.fixture(autouse=True)
def cleanup():
    yield
    MockRTC.RTC().destroy()


def test_init():
    """Test that the RTC.datetime is initialized with a time.struct_time"""
    RTC.init()

    mrtc: MockRTC = MockRTC.RTC()
    assert mrtc.datetime is not None, "Mock RTC datetime should be set"
    assert isinstance(
        mrtc.datetime, time.struct_time
    ), "Mock RTC datetime should be a time.struct_time instance"
