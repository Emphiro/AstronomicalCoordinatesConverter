import math

import numpy as np

from utils import angle_converter as ac

TIME_2000: float = 2451545.0
PI2: float = 2 * math.pi


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
    ra: float = ac.deg_to_rad(ra_deg) % PI2
    dec: float = ac.deg_to_rad(dec_deg) % PI2
    lat: float = ac.deg_to_rad(lat_deg) % PI2
    lon: float = ac.deg_to_rad(lon_deg) % PI2
    theta: float = earth_rot_angle(time_jd)
    era: float = ac.rad_to_deg(theta % PI2)
    theta: float = (theta + lon) % PI2
    [x, y, z] = compute_rx() @ compute_ry(lat) @ compute_rz(theta) @ angle_to_coords(ra, dec)

    el: float = math.acos(z)
    el = math.pi / 2 - el
    az: float = math.atan(y / x)
    if x < 0:
        az = az + math.pi
    elif x > 0 > y:
        az = az + PI2

    az_deg: float = ac.rad_to_deg(az)
    el_deg: float = ac.rad_to_deg(el)
    return [era, az_deg, el_deg]


