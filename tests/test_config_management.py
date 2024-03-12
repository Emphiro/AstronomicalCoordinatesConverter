from astronomical_data import config_management as conv

import math
from random import uniform
from math import floor

EPSILON = 1e-5


def equals(value1, value2):
    return value2 - EPSILON <= value1 <= value2 + EPSILON


def test_getter_setter():
    num_tests = 500
    ra = conv.get_ra()
    dec = conv.get_dec()
    lat = conv.get_lat()
    lon = conv.get_lon()

    for i in range(num_tests):
        deg = floor(uniform(0, 359))
        hour = floor(uniform(0, 23))
        min_value = floor(uniform(0, 59))
        sec = floor(uniform(0, 59))
        conv.set_dec(deg, min_value, sec)
        assert equals(conv.get_dec(), conv.dms_to_deg(deg, min_value, sec))
        conv.set_ra(hour, min_value, sec)
        assert equals(conv.get_ra(), conv.hms_to_deg(hour, min_value, sec))
        conv.set_lon(deg, min_value, sec)
        assert equals(conv.get_lon(), conv.dms_to_deg(deg, min_value, sec))
        conv.set_lat(deg, min_value, sec)
        assert equals(conv.get_lat(), conv.dms_to_deg(deg, min_value, sec))

    conv.set_ra(ra, single_value=True)
    conv.set_dec(dec, single_value=True)
    conv.set_lon(lon, single_value=True)
    conv.set_lat(lat, single_value=True)
    assert equals(conv.get_ra(), ra)
    assert equals(conv.get_dec(), dec)
    assert equals(conv.get_lat(), lat)
    assert equals(conv.get_lon(), lon)
    conv.set_time(2023, 1, 2, 0, 0, 0)
    assert equals(conv.get_time_jd(), 2459946.5)
    time = conv.get_time()
    conv.set_time_utc(time)
    assert equals(time.jd, conv.get_time_jd())
    print("test")
