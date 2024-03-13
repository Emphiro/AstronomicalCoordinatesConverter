
from astropy.time import Time

def normal_time_to_utc(year: int, month: int, day: int, hour: int, minutes: int, sec: float) -> Time:
    """convert time in year-month-day hour:minutes:seconds format to Time object"""
    return Time("{}-{}-{}T{}:{}:{}".format(year, month, day, hour, minutes, sec),
                format="isot", scale="utc")


def hours_from_julian_days(time: float) -> float:
    return ((time * 24) - 12) % 24
