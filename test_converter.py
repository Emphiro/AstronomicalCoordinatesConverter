import converter as conv
import math
from random import uniform
from math import floor
import subprocess
import time

EPSILON = 1e-3


def equals(value1, value2):
    return value2 - EPSILON <= value1 <= value2 + EPSILON


def test_conversions():
    num_tests = 500
    # deg_to_rad rad_to_deg
    assert equals(conv.deg_to_rad(180), math.pi)
    assert equals(conv.deg_to_rad(0), 0)
    for i in range(0, num_tests):
        rand = uniform(0, 360)
        assert equals(conv.rad_to_deg(conv.deg_to_rad(rand)), rand)
        rand = uniform(0, 2 * math.pi)
        assert equals(conv.deg_to_rad(conv.rad_to_deg(rand)), rand)

    # dms_to_deg deg_to_dms
    assert equals(conv.dms_to_deg(34, 2, 43), 34.045277)
    for i in range(0, num_tests):
        deg = floor(uniform(0, 359))
        min = floor(uniform(0, 59))
        sec = floor(uniform(0, 59))
        assert conv.deg_to_dms(conv.dms_to_deg(deg, min, sec)) == '{}° {}\' {:.2f}\"'.format(deg, min, sec)

    # hms_to_deg deg_to_hms
    for i in range(0, num_tests):
        deg = floor(uniform(0, 23))
        min = floor(uniform(0, 59))
        sec = floor(uniform(0, 59))
        assert conv.deg_to_hms(conv.hms_to_deg(deg, min, sec)) == '{}h {}m {:.2f}s'.format(deg, min, sec)

    # normal_time_to_utc
    assert str(conv.normal_time_to_utc(2023, 1, 23, 12, 3, 1)) == '2023-01-23T12:03:01.000'


def test_getter_setter():
    num_tests = 500
    ra = conv.get_ra()
    dec = conv.get_dec()
    lat = conv.get_lat()
    lon = conv.get_lon()

    for i in range(num_tests):
        deg = floor(uniform(0, 359))
        hour = floor(uniform(0, 23))
        min = floor(uniform(0, 59))
        sec = floor(uniform(0, 59))
        conv.set_dec(deg, min, sec)
        assert equals(conv.get_dec(), conv.dms_to_deg(deg, min, sec))
        conv.set_ra(hour, min, sec)
        assert equals(conv.get_ra(), conv.hms_to_deg(hour, min, sec))
        conv.set_lon(deg, min, sec)
        assert equals(conv.get_lon(), conv.dms_to_deg(deg, min, sec))
        conv.set_lat(deg, min, sec)
        assert equals(conv.get_lat(), conv.dms_to_deg(deg, min, sec))

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


def test_computation():
    time = conv.normal_time_to_utc(2020, 12, 23, 7, 34, 34.5).jd
    ra = conv.hms_to_deg(13, 37, 0.919)
    dec = conv.dms_to_deg(-29, 51, 56.74)
    lon = conv.dms_to_deg(10, 53, 22)
    lat = conv.dms_to_deg(49, 53, 6)
    [era, az, el] = conv.compute_azimuth_elevation(time, ra, dec, lon, lat)
    assert equals(era, 205.6840)
    assert equals(az, 190.8129)
    assert equals(el, 9.5009)


def write(p, line):
    assert p.poll() is None, "Program terminated early"
    p.stdin.write(line + "\n")
    p.stdin.flush()


def read(p):
    assert p.poll() is None, "Program terminated early"
    line = p.stdout.readline()
    return line


def test_io():
    for [command_name, function] in conv.executable_commands.items():
        with subprocess.Popen(
                "python3 converter.py -d",
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                universal_newlines=True,
        ) as p:

            num_lines = 3
            # Not working
            for i in range(num_lines):
                line = p.stdout.readline()
                #print(line)
            if command_name == "ctime":
                write(p, f"{command_name} 2022 10 10")
            elif command_name == "rm":
                write(p, f"{command_name} 1")
                write(p, "y")
            else:
                write(p, f"{command_name} 10")
            #print(command_name)
            line = read(p)
            #print(line)
            assert (line != ""), "Read empty line or closed output pipe"

            time.sleep(0.1)
            assert p.poll() is None, "Program terminated early"
            # write(p, "help")
            p.stdin.close()


test_io()
