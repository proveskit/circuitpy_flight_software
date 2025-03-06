import time

import mocks.circuitpython.rtc as MockRTC
from lib.pysquared.rtc.rtc_common import RTC


def test_init():
    """Test that the RTC.datetime is initialized with a time.struct_time"""
    RTC.init()

    mrtc: MockRTC = MockRTC.RTC()
    assert mrtc.datetime is not None, "Mock RTC datetime should be set"
    assert isinstance(
        mrtc.datetime, time.struct_time
    ), "Mock RTC datetime should be a time.struct_time instance"
