import math

PI2: float = 2 * math.pi
output_degrees: bool = False


def set_output_degrees(degrees: bool):
    global output_degrees
    output_degrees = degrees


def get_output_degrees() -> bool:
    return output_degrees


def switch_output_degrees() -> bool:
    global output_degrees
    output_degrees = not output_degrees
    return output_degrees


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
    degrees = (degrees / 360) * 24
    if output_degrees:
        return "{:.4f}°".format(degrees)
    [sign, degs, mins, secs] = convert_degrees(degrees)
    return "{}h {}m {:.2f}s".format(sign * degs, mins, secs)
