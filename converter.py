#!/usr/bin/env python3

import math
import sys
import textwrap
import pickle
from datetime import datetime
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


def deg_to_dms(degrees: float) -> str:
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


def deg_to_hms(degrees: float) -> str:
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




def get_ra() -> float:
    return current_config.ra


def get_dec() -> float:
    return current_config.dec


def get_lon():
    return current_config.lon


def get_lat() -> float:
    return current_config.lat


# Actual computation

def angle_to_coords(ra: float, dec: float) -> [float, float, float]:
    """convert spherical coordinates to cartesian coordinates"""
    return np.array([math.cos(ra) * math.cos(dec), math.sin(ra) * math.cos(dec), math.sin(dec)])


def earth_rot_angle(time_jd: float) -> float:
    """compute earth rotation angle (ERA) from time in julian days"""
    du = time_jd - TIME_2000
    angle = PI2 * (0.7790572732640 + 1.00273781191135448 * du)
    return angle


def compute_rz(theta: float):
    """compute rotation matrix around z-axis using theta in radians"""
    cos = math.cos(theta)
    sin = math.sin(theta)
    return np.array([[cos, sin, 0], [-sin, cos, 0], [0, 0, 1]])


def compute_rx():
    """compute rotation matrix around x-axis"""
    return np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])


def compute_ry(phi: float):
    """compute rotation matrix around y-axis using latitude in radians"""
    phi = (math.pi / 2) - phi % PI2
    cos = math.cos(phi)
    sin = math.sin(phi)
    return np.array([[cos, 0, -sin], [0, 1, 0], [sin, 0, cos]])


def compute_azimuth_elevation(time_jd: float, ra_deg: float, dec_deg: float, lon_deg: float, lat_deg: float) -> [float, float, float]:
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

    az_dms: str = deg_to_dms(rad_to_deg(az))
    el_dms: str = deg_to_dms(rad_to_deg(el))
    return [era, az_dms, el_dms]


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


# I/O functions


def print_solution(era, az, el):
    print("Era: {:.4f}\nAzimuth: {}\nElevation: {}".format(era, az, el))


def execute():
    """prints the era azimuth and elevation for the current configuration"""
    ex = current_config
    time_jd = ex.time.jd
    ra_deg = ex.ra
    dec_deg = ex.dec
    lon_deg = ex.lon
    lat_deg = ex.lat
    [era, az, el] = compute_azimuth_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
    print_solution(era, az, el)


# Global Variables (set in init_values)


output_degrees = False
use_current_time = False
# The Example testcases


configurations = [
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

current_config = Configuration(
        time=normal_time_to_utc(2021, 1, 7, 0, 0, 0),
        ra=hms_to_deg(2, 31, 49.09),
        dec=dms_to_deg(89, 15, 50.8),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6))


def main():
    execute()


if __name__ == "__main__":
    main()
