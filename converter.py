#!/usr/bin/env python3

import math
import sys
import textwrap
import pickle
from datetime import datetime
import numpy as np
from astropy.time import Time


# constants

TIME_2000 = 2451545.0
PI2 = 2 * math.pi
DEBUG_MODE = False

# date conversions

def normal_time_to_utc(year, month, day, hour, minutes, sec):
    """convert time in year-month-day hour:minutes:seconds format to Time object"""
    return Time("{}-{}-{}T{}:{}:{}".format(year, month, day, hour, minutes, sec),
                format="isot", scale="utc")


# angle conversions

def dms_to_deg(deg, minute, sec):
    """convert degrees, arcminutes and arcseconds to degrees"""
    sign = -1 if deg < 0 else 1
    deg = abs(deg)
    return sign * deg + sign * minute / 60 + sign * sec / (60 ** 2)


def hms_to_deg(hour, minute, sec):
    """convert hours, minutes and seconds to degrees"""
    sign = -1 if hour < 0 else 1
    hour = abs(hour)
    return ((sign * hour + sign * minute / 60 + sign * sec / (60 ** 2)) / 24) * 360


def angle_to_gmst(theta):
    return 86400 * (theta / PI2)


def deg_to_rad(degrees):
    """convert degrees to radians"""
    return (degrees / 360) * PI2


def rad_to_deg(rad):
    """convert radians to degrees"""
    return (rad / PI2) * 360


def deg_to_dms(degrees):
    """convert degrees to degrees, arcminutes and arcseconds if output_degrees = False"""
    if output_degrees:
        return "{:.4f}".format(degrees)
    sign = -1 if degrees < 0 else 1
    degrees = abs(degrees)
    degs = math.floor(degrees)
    mins = math.floor((degrees - degs) * 60)
    secs = (((degrees - degs) * 60) - mins) * 60
    # edge case: secs = 60.00
    if round(secs, 2) == 60.00:
        secs = 0
        mins += 1
    # edge case: mins = 60
    if mins == 60:
        mins = 0
        degrees += 1
    return "{}d {}m {:.2f}s".format(sign * degs, mins, secs)


def deg_to_hms(degrees):
    """convert degrees to hours, minutes and seconds if output_degrees = False"""
    if output_degrees:
        return "{:.4f}".format(degrees)
    sign = -1 if degrees < 0 else 1
    degrees = abs(degrees)
    degrees = (degrees / 360) * 24
    degs = math.floor(degrees)
    mins = math.floor((degrees - degs) * 60)
    secs = (((degrees - degs) * 60) - mins) * 60
    # edge case: secs = 60.00
    if round(secs, 2) == 60.00:
        secs = 0
        mins += 1
    # edge case: mins = 60
    if mins == 60:
        mins = 0
        degrees += 1
    return "{}h {}m {:.2f}s".format(sign * degs, mins, secs)


# Getter and Setter functions

def get_time():
    """Return an astropy time object"""
    if use_current_time:
        return Time(datetime.now())
    else:
        return current_config.time


def get_time_jd():
    """Return the time in julian days"""
    if use_current_time:
        return Time(datetime.now()).jd
    return current_config.time.jd


def set_time(*new_time, single_value=False):
    """new_time as *[year, month, day, hour, minute, second]"""
    if single_value:
        set_time_utc(new_time[0])
    global use_current_time
    use_current_time = False
    global current_config
    current_config.time = normal_time_to_utc(
        new_time[0], new_time[1], new_time[2], new_time[3], new_time[4], new_time[5])
    return current_config.time


def set_time_utc(new_time):
    """new_time as Time object"""
    global use_current_time
    use_current_time = False
    global current_config
    current_config.time = new_time


def set_ra(*new_ra, single_value=False):
    """new_ra as *[hours, minutes, seconds]"""
    global current_config
    if single_value:
        current_config.ra = new_ra[0]
        return deg_to_hms(current_config.ra)
    current_config.ra = hms_to_deg(new_ra[0], new_ra[1], new_ra[2])
    return deg_to_hms(current_config.ra)


def get_ra():
    return current_config.ra


def set_dec(*new_dec, single_value=False):
    """new_dec as *[degrees, arcminutes, arcseconds]"""
    global current_config
    if single_value:
        current_config.dec = new_dec[0]
        return deg_to_dms(current_config.dec)
    current_config.dec = dms_to_deg(new_dec[0], new_dec[1], new_dec[2])
    return deg_to_dms(current_config.dec)


def get_dec():
    return current_config.dec


def set_lon(*new_lon, single_value=False):
    """new_lon as *[degrees, arcminutes, arcseconds]"""
    global current_config
    if single_value:
        current_config.lon = new_lon[0]
        return deg_to_dms(current_config.lon)
    current_config.lon = dms_to_deg(new_lon[0], new_lon[1], new_lon[2])
    return deg_to_dms(current_config.lon)


def get_lon():
    return current_config.lon


def set_lat(*new_lat, single_value=False):
    """new_lat as *[degrees, arcminutes, arcseconds]"""
    global current_config
    if single_value:
        current_config.lat = new_lat[0]
        return deg_to_dms(current_config.lat)
    current_config.lat = dms_to_deg(new_lat[0], new_lat[1], new_lat[2])
    return deg_to_dms(current_config.lat)


def get_lat():
    return current_config.lat


# Actual computation

def angle_to_coords(ra, dec):
    """convert spherical coordinates to cartesian coordinates"""
    return np.array([math.cos(ra) * math.cos(dec), math.sin(ra) * math.cos(dec), math.sin(dec)])


def earth_rot_angle(time_jd):
    """compute earth rotation angle (ERA) from time in julian days"""
    du = time_jd - TIME_2000
    angle = PI2 * (0.7790572732640 + 1.00273781191135448 * du)
    return angle


def compute_rz(theta):
    """compute rotation matrix around z-axis using theta in radians"""
    cos = math.cos(theta)
    sin = math.sin(theta)
    return np.array([[cos, sin, 0], [-sin, cos, 0], [0, 0, 1]])


def compute_rx():
    """compute rotation matrix around x-axis"""
    return np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])


def compute_ry(phi):
    """compute rotation matrix around y-axis using latitude in radians"""
    phi = (math.pi / 2) - phi % PI2
    cos = math.cos(phi)
    sin = math.sin(phi)
    return np.array([[cos, 0, -sin], [0, 1, 0], [sin, 0, cos]])


def compute_azimuth_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg):
    """compute era, azimuth and elevation from time in julian days and
    right ascension, declination, longitude and latitude in degrees"""
    ra = deg_to_rad(ra_deg) % PI2
    dec = deg_to_rad(dec_deg) % PI2
    lat = deg_to_rad(lat_deg) % PI2
    lon = deg_to_rad(lon_deg) % PI2
    theta = earth_rot_angle(time_jd)
    era = rad_to_deg(theta % PI2)
    theta = (theta + lon) % PI2
    [x, y, z] = compute_rx() @ compute_ry(lat) @ compute_rz(theta) @ angle_to_coords(ra, dec)

    el = math.acos(z)
    el = math.pi / 2 - el
    az = math.atan(y / x)
    if x < 0:
        az = az + math.pi
    elif x > 0 > y:
        az = az + PI2

    az_dms = deg_to_dms(rad_to_deg(az))
    el_dms = deg_to_dms(rad_to_deg(el))
    return [era, az_dms, el_dms]


class Configuration:
    def __init__(self, time, ra, dec, lon, lat):
        self.time = time
        self.ra = ra
        self.dec = dec
        self.lon = lon
        self.lat = lat

    def __str__(self):
        return (f"Time: {self.time}\nRight Ascension: {deg_to_hms(self.ra)}\n"
                f"Declination: {deg_to_dms(self.dec)}\nLongitude: {deg_to_dms(self.lon)}"
                f"\nLatitude: {deg_to_dms(self.lat)}")


# The Example testcases

examples_old = [
    Configuration(
        time=normal_time_to_utc(2021, 2, 7, 22, 23, 24),
        ra=hms_to_deg(18, 18, 48),
        dec=dms_to_deg(-13, 48, 24),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    Configuration(
        time=normal_time_to_utc(2021, 1, 7, 0, 0, 0),
        ra=hms_to_deg(2, 31, 49.09),
        dec=dms_to_deg(89, 15, 50.8),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    Configuration(
        time=normal_time_to_utc(2020, 12, 23, 7, 34, 34.5),
        ra=hms_to_deg(13, 37, 0.919),
        dec=dms_to_deg(-29, 51, 56.74),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

]

configurations = [
    Configuration(
        time=normal_time_to_utc(2020, 12, 23, 7, 34, 34.5),
        ra=hms_to_deg(13, 37, 0.919),
        dec=dms_to_deg(-29, 51, 56.74),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    Configuration(
        time=normal_time_to_utc(2021, 2, 7, 22, 23, 24),
        ra=hms_to_deg(18, 18, 48),
        dec=dms_to_deg(-13, 48, 24),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    Configuration(
        time=normal_time_to_utc(2021, 1, 7, 0, 0, 0),
        ra=hms_to_deg(2, 31, 49.09),
        dec=dms_to_deg(89, 15, 50.8),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

]


# I/O functions

def save_to_file():
    with open('configurations.pkl', 'wb') as outp:
        pickle.dump(configurations, outp, 0)


def load_from_file():
    with open('configurations.pkl', 'rb') as inp:
        global configurations
        configurations = pickle.load(inp)


def add_config(input_string):
    ex = Configuration(
        time=get_time(),
        ra=get_ra(),
        dec=get_dec(),
        lon=get_lon(),
        lat=get_lat())
    configurations.append(ex)
    print("Saved as Configuration {}".format(len(configurations)))


def remove_config(input_string):
    """removes a configuration from the array"""
    global configurations
    num = input_string.split()[1] if len(input_string.split()) > 1 else None
    if num is None:
        num = input("Which configuration? ")
    try:
        num = int(num) - 1
    except ValueError:
        print("Please specify a configuration between 1 and {}".format(len(configurations)))
        return
    if len(configurations) > num >= 0:
        confirmation = input("Are you sure you want to delete configuration {}? (y/n)".format(num+1))
        if confirmation == "Y" or confirmation == "y":
            configurations.pop(num)
        else:
            return
    else:
        print("Please specify a configuration between 1 and {}".format(len(configurations)))
        return
    print("Successfully removed the specified configuration")


def load(input_string):
    """loads a configuration to be the currently used value"""
    num = input_string.split()[1] if len(input_string.split()) > 1 else None
    if num is None:
        num = input("Which configuration? ")
    try:
        num = int(num) - 1
    except ValueError:
        print("Please specify a configuration between 1 and {}".format(len(configurations)))
        return
    if len(configurations) > num >= 0:
        ex = configurations[num]
        set_time_utc(new_time=ex.time)
        set_ra(ex.ra, single_value=True)
        set_dec(ex.dec, single_value=True)
        set_lon(ex.lon, single_value=True)
        set_lat(ex.lat, single_value=True)
    else:
        print("Please specify a configuration between 1 and {}".format(len(configurations)))
        return
    list_values("")


def print_solution(era, az, el):
    print("Era: {:.4f}\nAzimuth: {}\nElevation: {}".format(era, az, el))


def change_value(input_string):
    types = {
        "clat": [set_lat, "dms", "Latitude"],
        "clon": [set_lon, "dms", "Longitude"],
        "cdec": [set_dec, "dms", "Declination"],
        "cra": [set_ra, "hms", "Right Ascension"],
        "ctime": [set_time, "time", "Time"]
    }
    questions_list = {
        "hms": ["hours? ", "minutes? ", "seconds? "],
        "dms": ["degrees? ", "arcminutes? ", "arcseconds? "],
        "time": ["year? ", "month? ", "day? ", "hour? ", "minute? ", "second? "]
    }

    input_arr = input_string.split()
    set_func = types[input_arr[0]][0]
    request_type = types[input_arr[0]][1]
    name = types[input_arr[0]][2]

    questions = questions_list[request_type]
    values = [0, 0, 0, 0, 0, 0]
    in_degrees = (len(input_arr) == 2) and request_type != "time"
    try:
        if in_degrees:
            values[0] = float(input_arr[1])
        elif 1 < len(input_arr) <= len(questions) + 1:
            for [i, value] in enumerate(input_arr[1:]):
                values[i] = int(value)
        else:
            for [i, question] in enumerate(questions[:-1]):
                answer = input(question)
                if answer == '':
                    values[i] = 0
                else:
                    values[i] = int(answer)
            answer = input(questions[-1])
            if answer == '':
                values[len(questions) - 1] = 0
            else:
                values[len(questions) - 1] = float(answer)

    except ValueError as er:
        print(er)
        print("Invalid Value. Please try again")
        change_value(input_string.split()[0])
        return
    except EOFError:
        return
    try:
        value = set_func(*values, single_value=in_degrees)
    except ValueError as er:
        print(er)
        print("Invalid Value. Please try again")
        change_value(input_string.split()[0])
        return
    print("Set {} to {}".format(name, value))


def reset_location(input_string):
    set_lon(10, 53, 22)
    set_lat(49, 53, 6)
    print("set Location to remeis observatory")


def reset_time(input_string):
    global use_current_time
    use_current_time = True
    print("set Time to current time")


def list_values(input_string):
    print("Time set to {}".format(get_time()))
    print("Right Ascension set to {}".format(deg_to_hms(get_ra())))
    print("Declination set to {}".format(deg_to_dms(get_dec())))
    print("Longitude set to {}".format(deg_to_dms(get_lon())))
    print("Latitude set to {}".format(deg_to_dms(get_lat())))


def list_configurations(input_string):
    for (i, ex) in enumerate(configurations):
        print("Configuration {}:".format(i+1))
        print(textwrap.indent(str(ex), "    "))


def execute(input_string):
    if len(input_string.split()) > 1:
        exec_configuration(input_string.split()[1])
        return
    time_jd = get_time_jd()
    ra_deg = get_ra()
    dec_deg = get_dec()
    lon_deg = get_lon()
    lat_deg = get_lat()
    [era, az, el] = compute_azimuth_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
    print_solution(era, az, el)


def change_output_mode(input_string):
    global output_degrees
    output_degrees = not output_degrees
    output = "Output will be given in degrees" if output_degrees else \
        "Output will be given in degrees arc-minutes and arc-seconds"
    print(output)


def exec_configuration(num):
    """prints the configuration specified by the integer num"""
    if num is None:
        num = input("Which configuration? ")
    try:
        num = int(num) - 1
    except ValueError:
        print("Please specify an configuration between 1 and {}".format(len(configurations)))
        return
    if len(configurations) > num >= 0:
        ex = configurations[num]
        time_jd = ex.time.jd
        ra_deg = ex.ra
        dec_deg = ex.dec
        lon_deg = ex.lon
        lat_deg = ex.lat
        [era, az, el] = compute_azimuth_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
        print_solution(era, az, el)
    else:
        print("Please specify an configuration between 1 and {}".format(len(configurations)))


def print_help(input_string):
    print("Available commands:")
    for [command, description] in available_commands.items():
        print(command + ":")
        print(textwrap.indent(description, "    "))


def init_values():
    global use_current_time
    use_current_time = True
    set_time(2020, 12, 23, 7, 34, 34.5)
    set_ra(13, 37, 0.919)
    set_dec(-29, 51, 56.74)
    set_lon(10, 53, 22)
    set_lat(49, 53, 6)


def not_available(input_string):
    print("Someone has not yet implemented this function :(")


available_commands = {
    "ctime": "Change the time",
    "cra": "Change the right ascension",
    "cdec": "Change the declination",
    "clon": "Change the longitude",
    "clat": "Change the latitude",
    "rloc": "Change the location to remeis observatory",
    "rtime": "Change the time to the current time",
    "ex": "Calculate the Era, Azimuth and Elevation for the currently set values",
    "ls": "Show the currently set values",
    "save": "Save the current configurations",
    "load": "Load one of the saved configurations",
    "lse": "List all the saved configurations",
    "rm": "Remove the selected configuration",
    "co": "Toggles output mode between degrees and degree:arc-minute:arc-second",
}

executable_commands = {
    "help": print_help,
    "ctime": change_value,
    "cra": change_value,
    "cdec": change_value,
    "clon": change_value,
    "clat": change_value,
    "rloc": reset_location,
    "rtime": reset_time,
    "ex": execute,
    "ls": list_values,
    "save": add_config,
    "load": load,
    "lse": list_configurations,
    "rm": remove_config,
    "co": change_output_mode,
    #"test": 1
}


def input_loop():
    input_string = input("> ")
    if len(input_string) == 0:
        return
    try:
        command = executable_commands[input_string.split()[0]]
        command(input_string)
    except KeyError:
        print("No matching command found. Type help for a list of commands")


# Global Variables (set in init_values)

output_degrees = False
use_current_time = True
current_config = Configuration(
        time=normal_time_to_utc(2021, 1, 7, 0, 0, 0),
        ra=hms_to_deg(2, 31, 49.09),
        dec=dms_to_deg(89, 15, 50.8),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6))


def main():
    global DEBUG_MODE
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "-e":
            exec_configuration((sys.argv[2] if len(sys.argv) > 2 else None))
            return
        if arg == "-h":
            print_help("")
            return
        if arg == "-d":
            DEBUG_MODE = True
    init_values()

    if not DEBUG_MODE:
        try:
            load_from_file()
        except FileNotFoundError:
            global configurations
            configurations = examples_old
            print("No file was found. Loading basic configurations", file=sys.stderr)
    else:
        configurations = examples_old
    print("Welcome to this coordinates converter program!")
    print()
    print("Type help for a list of commands")
    while 1:
        try:
            input_loop()
        except EOFError:
            break
        except KeyboardInterrupt:
            break
    if not DEBUG_MODE:
        save_to_file()


if __name__ == "__main__":
    main()
