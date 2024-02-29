#!/usr/bin/env python3

import math
import sys
import textwrap
import pickle
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time

# constants

TIME_2000: float = 2451545.0
PI2: float = 2 * math.pi
DEBUG_MODE: bool = False


# date conversions


def normal_time_to_utc(year: int, month: int, day: int, hour: int, minutes: int, sec: float) -> Time:
    """convert time in year-month-day hour:minutes:seconds format to Time object"""
    return Time("{}-{}-{}T{}:{}:{}".format(year, month, day, hour, minutes, sec),
                format="isot", scale="utc")


# angle conversions

def dms_to_deg(deg: int, minute: int, sec: float) -> float:
    """convert degrees, arcminutes and arcseconds to degrees"""
    sign = -1 if deg < 0 else 1
    deg = abs(deg)
    return sign * deg + sign * minute / 60 + sign * sec / (60 ** 2)


def hms_to_deg(hour: int, minute: int, sec: float) -> float:
    """convert hours, minutes and seconds to degrees"""
    sign = -1 if hour < 0 else 1
    hour = abs(hour)
    return ((sign * hour + sign * minute / 60 + sign * sec / (60 ** 2)) / 24) * 360


def angle_to_gmst(theta: float) -> float:
    return 86400 * (theta / PI2)


def deg_to_rad(degrees: float) -> float:
    """convert degrees to radians"""
    return (degrees / 360) * PI2


def rad_to_deg(rad: float) -> float:
    """convert radians to degrees"""
    return (rad / PI2) * 360


def convert_degrees(degrees: float) -> list:
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
    return [sign, degs, mins, secs]


def deg_to_dms(degrees: float) -> str:
    """convert degrees to degrees, arcminutes and arcseconds if output_degrees = False"""
    if output_degrees:
        return "{:.4f}°".format(degrees)
    [sign, degs, mins, secs] = convert_degrees(degrees)
    return "{}° {}' {:.2f}\"".format(sign * degs, mins, secs)


def deg_to_hms(degrees: float) -> str:
    """convert degrees to hours, minutes and seconds if output_degrees = False"""
    if output_degrees:
        return "{:.4f}°".format(degrees)
    [sign, degs, mins, secs] = convert_degrees(degrees)
    return "{}h {}m {:.2f}s".format(sign * degs, mins, secs)


# Getter and Setter functions

def get_time() -> Time:
    """Return an astropy time object"""
    if use_current_time:
        return Time(datetime.now())
    else:
        return current_config.time


def get_time_jd() -> float:
    """Return the time in julian days"""
    if use_current_time:
        return Time(datetime.now()).jd
    return current_config.time.jd


def set_time(*new_time, single_value=False) -> Time:
    """new_time as *[year, month, day, hour, minute, second]"""
    if single_value:
        set_time_utc(new_time[0])
    global use_current_time
    use_current_time = False
    global current_config
    current_config.time = normal_time_to_utc(
        new_time[0], new_time[1], new_time[2], new_time[3], new_time[4], new_time[5])
    return current_config.time


def set_time_utc(new_time: Time):
    """new_time as Time object"""
    global use_current_time
    use_current_time = False
    global current_config
    current_config.time = new_time


def set_ra(*new_ra: [float, float, float], single_value=False) -> str:
    """new_ra as *[hours, minutes, seconds]"""
    global current_config
    if single_value:
        current_config.ra = new_ra[0]
        return deg_to_hms(current_config.ra)
    current_config.ra = hms_to_deg(new_ra[0], new_ra[1], new_ra[2])
    return deg_to_hms(current_config.ra)


def get_ra() -> float:
    return current_config.ra


def set_dec(*new_dec: [float, float, float], single_value=False) -> str:
    """new_dec as *[degrees, arcminutes, arcseconds]"""
    global current_config
    if single_value:
        current_config.dec = new_dec[0]
        return deg_to_dms(current_config.dec)
    current_config.dec = dms_to_deg(new_dec[0], new_dec[1], new_dec[2])
    return deg_to_dms(current_config.dec)


def get_dec() -> float:
    return current_config.dec


def set_lon(*new_lon: [float, float, float], single_value=False) -> str:
    """new_lon as *[degrees, arcminutes, arcseconds]"""
    global current_config
    if single_value:
        current_config.lon = new_lon[0]
        return deg_to_dms(current_config.lon)
    current_config.lon = dms_to_deg(new_lon[0], new_lon[1], new_lon[2])
    return deg_to_dms(current_config.lon)


def get_lon():
    return current_config.lon


def set_lat(*new_lat: [float, float, float], single_value=False) -> str:
    """new_lat as *[degrees, arcminutes, arcseconds]"""
    global current_config
    if single_value:
        current_config.lat = new_lat[0]
        return deg_to_dms(current_config.lat)
    current_config.lat = dms_to_deg(new_lat[0], new_lat[1], new_lat[2])
    return deg_to_dms(current_config.lat)


def get_lat() -> float:
    return current_config.lat


# Actual computation

def angle_to_coords(ra: float, dec: float) -> np.ndarray:
    """convert spherical coordinates to cartesian coordinates"""
    return np.array([math.cos(ra) * math.cos(dec), math.sin(ra) * math.cos(dec), math.sin(dec)])


def earth_rot_angle(time_jd: float) -> float:
    """compute earth rotation angle (ERA) from time in julian days"""
    du = time_jd - TIME_2000
    angle = PI2 * (0.7790572732640 + 1.00273781191135448 * du)
    return angle


def compute_rz(theta: float) -> np.ndarray:
    """compute rotation matrix around z-axis using theta in radians"""
    cos = math.cos(theta)
    sin = math.sin(theta)
    return np.array([[cos, sin, 0], [-sin, cos, 0], [0, 0, 1]])


def compute_rx() -> np.ndarray:
    """compute rotation matrix around x-axis"""
    return np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])


def compute_ry(phi: float) -> np.ndarray:
    """compute rotation matrix around y-axis using latitude in radians"""
    phi = (math.pi / 2) - phi % PI2
    cos = math.cos(phi)
    sin = math.sin(phi)
    return np.array([[cos, 0, -sin], [0, 1, 0], [sin, 0, cos]])


def compute_azimuth_elevation(time_jd: float, ra_deg: float, dec_deg: float,
                              lon_deg: float, lat_deg: float) -> list:
    """compute era, azimuth and elevation from time in julian days and
    right ascension, declination, longitude and latitude in degrees"""
    ra: float = deg_to_rad(ra_deg) % PI2
    dec: float = deg_to_rad(dec_deg) % PI2
    lat: float = deg_to_rad(lat_deg) % PI2
    lon: float = deg_to_rad(lon_deg) % PI2
    theta: float = earth_rot_angle(time_jd)
    era: float = rad_to_deg(theta % PI2)
    theta: float = (theta + lon) % PI2
    [x, y, z] = compute_rx() @ compute_ry(lat) @ compute_rz(theta) @ angle_to_coords(ra, dec)

    el: float = math.acos(z)
    el = math.pi / 2 - el
    az: float = math.atan(y / x)
    if x < 0:
        az = az + math.pi
    elif x > 0 > y:
        az = az + PI2

    az_deg: float = rad_to_deg(az)
    el_deg: float = rad_to_deg(el)
    return [era, az_deg, el_deg]


class Configuration:
    def __init__(self, time, ra, dec, lon, lat):
        self.time: Time = time
        self.ra: float = ra
        self.dec: float = dec
        self.lon: float = lon
        self.lat: float = lat

    def __str__(self):
        return (f"Time: {self.time}\nRight Ascension: {deg_to_hms(self.ra)}\n"
                f"Declination: {deg_to_dms(self.dec)}\nLongitude: {deg_to_dms(self.lon)}"
                f"\nLatitude: {deg_to_dms(self.lat)}")


# The Example testcases

examples_old = {
    "config1": Configuration(
        time=normal_time_to_utc(2021, 2, 7, 22, 23, 24),
        ra=hms_to_deg(18, 18, 48),
        dec=dms_to_deg(-13, 48, 24),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    "config2": Configuration(
        time=normal_time_to_utc(2021, 1, 7, 0, 0, 0),
        ra=hms_to_deg(2, 31, 49.09),
        dec=dms_to_deg(89, 15, 50.8),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    "config3": Configuration(
        time=normal_time_to_utc(2020, 12, 23, 7, 34, 34.5),
        ra=hms_to_deg(13, 37, 0.919),
        dec=dms_to_deg(-29, 51, 56.74),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    "m38": Configuration(
        time=normal_time_to_utc(2024, 3, 13, 0, 0, 0),
        ra=hms_to_deg(5, 28, 42.5),
        dec=dms_to_deg(35, 51, 18),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

}

configurations = {
    "config1": Configuration(
        time=normal_time_to_utc(2021, 2, 7, 22, 23, 24),
        ra=hms_to_deg(18, 18, 48),
        dec=dms_to_deg(-13, 48, 24),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),
}


# I/O functions
def plot_config(config: Configuration, length: float, step_size: float) -> list:
    assert step_size > 0
    time: float = config.time.jd
    time_end: float = time + length / 24
    ra: float = config.ra
    dec: float = config.dec
    lon: float = config.lon
    lat: float = config.lat
    values: list = []
    while time < time_end:
        [era, az, el] = compute_azimuth_elevation(time, ra, dec, lon, lat)
        values.append((time, era, az, el))
        time += step_size / 24
    return values


def print_plot(values: list):
    for (i, (time, era, az, el)) in enumerate(values):
        time_utc: Time = Time(time, format="jd")
        time_utc.format = "iso"
        print(f"{i} {time_utc}:")
        print_solution(era, az, el)


def show_polar_plot(values: list, config_name: str, draw_lines=False):
    plt.style.use("_mpl-gallery")
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    angles = []
    radii = []
    colors = []
    i = range(0, len(values))
    for (i, (time, era, az, el)) in enumerate(values):
        radius: float = 90 - el
        angle: float = deg_to_rad(az)
        color = [0, 0, i / len(values)]
        angles.append(angle)
        radii.append(radius)
        colors.append(color)

    times = np.linspace(0, 10, len(angles))

    if draw_lines:
        ax.plot(angles, radii)
    else:
        ax.scatter(angles, radii, c=times, cmap='viridis')
    time_start: Time = Time(values[0][0], format="jd")
    time_start.format = "iso"
    time_end: Time = Time(values[-1][0], format="jd")
    time_end.format = "iso"
    ax.set_rticks([45, 90, 135, 180])
    ax.grid(True)
    plt.text(-0.30, 0.10,
             f"Plotting {config_name}\nfrom: {time_start}\nto:   {time_end}",
             transform=plt.gca().transAxes, fontsize=12,
             verticalalignment='bottom', horizontalalignment='left')
    plt.subplots_adjust(left=0.05, bottom=0.05, top=0.95)
    plt.show()


def show_simple_plot(values: list, config_name: str):
    plt.style.use("_mpl-gallery")
    fig, ax = plt.subplots()
    t = []
    y1 = []
    y2 = []
    for(time, era, az, el) in values:
        t.append((time*24) % 24)
        y1.append(az)
        y2.append(el)
    ax.scatter(t, y1, label="Azimuth", color="lime")
    ax.scatter(t, y2, label="Elevation", color="royalblue")
    ax.set(xlabel='time (h)', ylabel='Azimuth and Elevation (degrees)',
           title='Azimuth and Elevation plotted against time')
    plt.subplots_adjust(left=0.05, bottom=0.05, top=0.925)
    time_start: Time = Time(values[0][0], format="jd")
    time_start.format = "iso"
    time_end: Time = Time(values[-1][0], format="jd")
    time_end.format = "iso"
    ax.set_title(f"Plotting {config_name}\nfrom: {time_start}\nto:   {time_end}")
    ax.grid(True)
    ax.set_yticks([-90, -45, 0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax.axhline(y=360, color="lime")
    ax.axhline(y=-90, color="royalblue")
    ax.axhline(y=0, color="lime")
    ax.axhline(y=90, color="royalblue")
    ax.set_xticks([0, 6, 12, 28, 24])
    ax.legend()
    plt.show()


def plot_input(input_string: str):
    input_array = input_string.split("\"")
    config_name = None
    if len(input_array) == 3:
        config_name = input_array[1]
        input_string = " ".join([input_array[0],"name", input_array[2]])

    input_array = input_string.split()

    name: str = input_array[0]
    is_verbose = "-v" in input_array
    is_simple = "-s" in input_array
    draw_lines: bool = "-l" in input_array
    if len(input_array) < 2:
        print("not enough arguments")
        print("Usage: " + usage[name])
        return
    if config_name is None:
        config_name = input_array[1]
    try:
        adjusted_len = len(input_array) - is_verbose - draw_lines - is_simple
        end = float(input_array[2]) if adjusted_len > 2 else 24
        if adjusted_len < 3:
            step_size = 1
        elif adjusted_len < 4:
            step_size = float(input_array[2])
        else:
            step_size = float(input_array[3])
    except ValueError:
        print("Invalid value for end or step_size given")
        print("Usage: " + usage[name])
        return
    if config_name not in configurations:
        print(f"{config_name} is not a saved configuration")
        return
    print(f"step_size {step_size}, config name: {config_name}, end: {end}")
    values = plot_config(configurations[config_name], end, step_size)
    if is_verbose:
        print_plot(values)
    if is_simple:
        show_simple_plot(values, config_name)
    else:
        show_polar_plot(values, config_name, draw_lines)


def save_to_file():
    with open('configurations.pkl', 'wb') as outp:
        pickle.dump(configurations, outp, 0)


def load_from_file():
    with open('configurations.pkl', 'rb') as inp:
        global configurations
        configurations = pickle.load(inp)


def add_config(name=None):
    ex = Configuration(
        time=get_time(),
        ra=get_ra(),
        dec=get_dec(),
        lon=get_lon(),
        lat=get_lat())
    count = 1
    if name is None:
        name = f"config{count}"
        while name in configurations:
            count += 1
            name = f"config{count}"

    if name in configurations:
        return None

    configurations.update({name: ex})
    return name


def add_config_input(input_string: str):
    input_array = input_string.split()
    if len(input_array) > 1:
        config_name = " ".join(input_string.split()[1:])
        name = add_config(config_name)
    else:
        name = add_config()

    if name is not None:
        print("Saved as Configuration \"{}\"".format(name))
    else:
        print("There is already a configuration named \"{}\"".format(input_array[1]))


def remove_config(config: str):
    configurations.pop(config)


def remove_config_input(input_string: str):
    """removes a configuration from the array"""
    config_name = " ".join(input_string.split()[1:]) if len(input_string.split()) > 1 else None
    if config_name is None:
        config_name = input("Which configuration? ")

    if config_name in configurations:
        confirmation: str = input("Are you sure you want to delete configuration {}? (y/n) ".
                                  format(config_name))
        if confirmation.lower() == "y":
            remove_config(config_name)
        else:
            return
    else:
        print("Please specify an existing configuration name")
        return
    print("Successfully removed the specified configuration")


def load(config_name: str):
    ex = configurations[config_name]
    set_time_utc(new_time=ex.time)
    set_ra(ex.ra, single_value=True)
    set_dec(ex.dec, single_value=True)
    set_lon(ex.lon, single_value=True)
    set_lat(ex.lat, single_value=True)


def load_input(input_string: str):
    """loads a configuration to be the currently used value"""
    config_name = " ".join(input_string.split()[1:]) if len(input_string.split()) > 1 else None
    if config_name is None:
        config_name = input("Which configuration? ")

    if config_name in configurations:
        load(config_name)
    else:
        print("Please specify an existing configuration name")
        return
    print(config_name)
    list_values()


def print_solution(era, az, el):
    print("Era: {:.4f}\nAzimuth: {}\nElevation: {}".format(
        era, deg_to_dms(az), deg_to_dms(el)))


def change_value_input(input_string: str):
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
        change_value_input(input_string.split()[0])
        return
    except EOFError:
        print()
        return
    try:
        value = set_func(*values, single_value=in_degrees)
    except ValueError as er:
        print(er)
        print("Invalid Value. Please try again")
        change_value_input(input_string.split()[0])
        return
    print("Set {} to {}".format(name, value))


def reset_location():
    set_lon(10, 53, 22)
    set_lat(49, 53, 6)


def reset_location_input(input_string: None):
    reset_location()
    print("set Location to remeis observatory")


def reset_time():
    global use_current_time
    use_current_time = True


def reset_time_input(input_string: None):
    reset_time()
    print("set Time to current time")


def list_values():
    print("Time set to {}".format(get_time()))
    print("Right Ascension set to {}".format(deg_to_hms(get_ra())))
    print("Declination set to {}".format(deg_to_dms(get_dec())))
    print("Longitude set to {}".format(deg_to_dms(get_lon())))
    print("Latitude set to {}".format(deg_to_dms(get_lat())))


def list_values_input(input_string: None):
    list_values()


def list_configurations():
    for (name, config) in configurations.items():
        print("Configuration {}:".format(name))
        print(textwrap.indent(str(config), "    "))


def list_configurations_input(input_string):
    list_configurations()


def execute() -> list:
    time_jd = get_time_jd()
    ra_deg = get_ra()
    dec_deg = get_dec()
    lon_deg = get_lon()
    lat_deg = get_lat()
    [era, az, el] = compute_azimuth_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
    return [era, az, el]


def execute_input(input_string: str):
    if len(input_string.split()) > 1:
        exec_configuration_input(" ".join(input_string.split()[1:]))
        return
    [era, az, el] = execute()
    print_solution(era, az, el)


def change_output_mode() -> bool:
    global output_degrees
    output_degrees = not output_degrees
    return output_degrees


def change_output_mode_input(input_string):
    change_output_mode()
    output = "Output will be given in degrees" if output_degrees else \
        "Output will be given in degrees arc-minutes and arc-seconds"
    print(output)


def exec_configuration(config_name: str) -> list:
    ex = configurations[config_name]
    time_jd = ex.time.jd
    ra_deg = ex.ra
    dec_deg = ex.dec
    lon_deg = ex.lon
    lat_deg = ex.lat
    [era, az, el] = compute_azimuth_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
    return [era, az, el]


def exec_configuration_input(config_name):
    """prints the configuration specified by the string config_name"""
    if config_name is None:
        config_name = input("Which configuration? ")

    if config_name in configurations:
        [era, az, el] = exec_configuration(config_name)
        print_solution(era, az, el)
    else:
        print("Please specify an existing configuration")


def print_help_input(input_string):
    print("Available commands:")
    for [command, description] in available_commands.items():
        print(command + ":")
        usage_str = "Usage: " + usage[command]
        print(textwrap.indent(usage_str, "       "))
        print(textwrap.indent(description, "    "))


def init_values():
    global use_current_time
    use_current_time = True
    set_time(2020, 12, 23, 7, 34, 34.5)
    set_ra(13, 37, 0.919)
    set_dec(-29, 51, 56.74)
    set_lon(10, 53, 22)
    set_lat(49, 53, 6)
    set_lat(49, 53, 6)


def not_available_input(input_string):
    print("Someone has not yet implemented this function :(")


available_commands = {
    "ctime": "Change the time",
    "cra": "Change the right ascension",
    "cdec": "Change the declination",
    "clon": "Change the longitude",
    "clat": "Change the latitude",
    "rloc": "Change the location to remeis observatory",
    "rtime": "Change the time to the current time",
    "ex": "Calculate the Era, Azimuth \nand Elevation for the currently set values",
    "ls": "Show the currently set values",
    "save": "Save the current configurations",
    "load": "Load one of the saved configurations",
    "lse": "List all the saved configurations",
    "rm": "Remove the selected configuration",
    "co": "Toggles output mode between degrees and degree:arc-minute:arc-second",
    "plot": "Plots the values of the selected configuration for [length] hours with"
            " step size [time_step]"
            "\n  -s: Draw a simple plot instead of the polar plot"
            "\n  -v: All the calculated values will be printed to the console"
            "\n  -l: Draw lines between the calculated values"
}

usage = {
    "ctime": "ctime [year:int] [month:int] [day:int] [hour:int] [minute:int] [second:int]",
    "cra": "cra [hours] [minutes] [seconds]",
    "cdec": "cdec [degrees] [arc-minutes] [arc-seconds]",
    "clon": "clon [degrees] [arc-minutes] [arc-seconds]",
    "clat": "clat [degrees] [arc-minutes] [arc-seconds]",
    "rloc": "rloc",
    "rtime": "rtime",
    "ex": "ex [config_name:str]",
    "ls": "ls",
    "save": "save config_name:str",
    "load": "load config_name:str",
    "lse": "lse",
    "rm": "rm config_name:str",
    "co": "co",
    "plot": "plot config_name:str [length:float] [time_step: float] [-s] [-v] [-d]"
}

executable_commands = {
    "help": print_help_input,
    "ctime": change_value_input,
    "cra": change_value_input,
    "cdec": change_value_input,
    "clon": change_value_input,
    "clat": change_value_input,
    "rloc": reset_location_input,
    "rtime": reset_time_input,
    "ex": execute_input,
    "ls": list_values_input,
    "save": add_config_input,
    "load": load_input,
    "lse": list_configurations_input,
    "rm": remove_config_input,
    "co": change_output_mode_input,
    "plot": plot_input,
}


def input_loop():
    input_string = input("> ")
    if len(input_string) == 0:
        return
    command_name: str = input_string.split()[0]
    if command_name in executable_commands:
        command = executable_commands[command_name]
        command(input_string)
    else:
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
            exec_configuration_input((sys.argv[2] if len(sys.argv) > 2 else None))
            return
        if arg == "-h":
            print_help_input("")
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
