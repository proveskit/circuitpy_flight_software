import time

try:
    import rtc
except ImportError:
    import mocks.circuitpython.rtc as rtc


class RP2040RTC:
    """
    Class for interfacing with the RP2040's Real Time Clock (RTC)
    """

    @staticmethod
    def set_time(
        year: int,
        month: int,
        date: int,
        hour: int,
        minute: int,
        second: int,
        day_of_week: int,
    ) -> None:
        """
        Updates the RP2040's Real Time Clock (RTC) to the date and time passed

        :param year: The year value (0-9999)
        :param month: The month value (1-12)
        :param date: The date value (1-31)
        :param hour: The hour value (0-23)
        :param minute: The minute value (0-59)
        :param second: The second value (0-59)
        :param day_of_week: The nth day of the week (0-6), where 0 represents Sunday and 6 represents Saturday
        """
        rp2040_rtc = rtc.RTC()
        rp2040_rtc.datetime = time.struct_time(
            (year, month, date, hour, minute, second, day_of_week, -1, -1)
        )
