from computations import computation as comp
from utils.angle_converter import *
from utils.date_converter import *
EPSILON = 1e-3


def equals(value1, value2):
    return value2 - EPSILON <= value1 <= value2 + EPSILON


def test_computation():
    time = normal_time_to_utc(2020, 12, 23, 7, 34, 34.5).jd
    ra = hms_to_deg(13, 37, 0.919)
    dec = dms_to_deg(-29, 51, 56.74)
    lon = dms_to_deg(10, 53, 22)
    lat = dms_to_deg(49, 53, 6)
    [era, az, el] = comp.compute_azimuth_elevation(time, ra, dec, lon, lat)
    assert equals(era, 205.6840)
    assert equals(az, 190.8129)
    assert equals(el, 9.5009)