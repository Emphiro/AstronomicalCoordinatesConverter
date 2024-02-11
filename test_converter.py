import converter as conv
import math
from random import uniform
from math import floor
EPSILON = 1e-3

def equals(value1, value2):
    return value2 - EPSILON <= value1 <= value1 + EPSILON

def test_convertions():
    num_tests = 500
    #deg_to_rad rad_to_deg
    assert equals(conv.deg_to_rad(180), math.pi)
    assert equals(conv.deg_to_rad(0), 0)
    for i in range(0, num_tests):
        rand = uniform(0, 360)
        assert equals(conv.rad_to_deg(conv.deg_to_rad(rand)), rand)
        rand = uniform(0, 2 * math.pi)
        assert equals(conv.deg_to_rad(conv.rad_to_deg(rand)), rand)
    #dms_to_deg deg_to_dms
    assert equals(conv.dms_to_deg(34, 2, 43), 34.045277)
    for i in range(0, num_tests):
        deg = floor(uniform(0, 359))
        min = floor(uniform(0, 59))
        sec = floor(uniform(0, 59))
        assert conv.deg_to_dms(conv.dms_to_deg(deg, min, sec)) == '{}d {}m {:.2f}s'.format(deg, min, sec)

    #hms_to_deg deg_to_hms
    for i in range(0, num_tests):
        deg = floor(uniform(0, 23))
        min = floor(uniform(0, 59))
        sec = floor(uniform(0, 59))
        assert conv.deg_to_hms(conv.hms_to_deg(deg, min, sec)) == '{}h {}m {:.2f}s'.format(deg, min, sec)

    
    #normal_time_to_utc
    assert str(conv.normal_time_to_utc(2023, 1, 23, 12, 3, 1)) == '2023-01-23T12:03:01.000' 



def test_getter_setter():
    rand = uniform(0, 20)

def test_computation():
    assert conv.deg_to_rad(180) == math.pi
    