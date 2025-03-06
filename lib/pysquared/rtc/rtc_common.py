import time

try:
    import rtc
except ImportError:
    import mocks.circuitpython.rtc as rtc


class RTC:
    """
    Common class for interfacing with the Real Time Clock (RTC)
    """

    @staticmethod
    def init() -> None:
        """
        Initialize the RTC

        Required on every boot to ensure the RTC is ready for use
        """
        rp2040_rtc = rtc.RTC()
        rp2040_rtc.datetime = time.localtime()
        print(f"RTC initialized with time: {rp2040_rtc.datetime}")
