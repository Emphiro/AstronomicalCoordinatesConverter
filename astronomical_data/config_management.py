from astronomical_data.configuration import Configuration
from astronomical_data import simbad_inteface as si
from astronomical_data import save_and_load as sl
from utils.angle_converter import *
from utils import date_converter as dc
from computations import computation as comp

from datetime import datetime

from astropy.time import Time

use_current_time = True

current_config = Configuration(
    time=dc.normal_time_to_utc(2021, 1, 7, 0, 0, 0),
    ra=hms_to_deg(2, 31, 49.09),
    dec=dms_to_deg(89, 15, 50.8),
    lon=dms_to_deg(10, 53, 22),
    lat=dms_to_deg(49, 53, 6))

configurations = {
    "config1": Configuration(
        time=dc.normal_time_to_utc(2021, 2, 7, 22, 23, 24),
        ra=hms_to_deg(18, 18, 48),
        dec=dms_to_deg(-13, 48, 24),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),
}

# The Example testcases

examples_old = {
    "config1": Configuration(
        time=dc.normal_time_to_utc(2021, 2, 7, 22, 23, 24),
        ra=hms_to_deg(18, 18, 48),
        dec=dms_to_deg(-13, 48, 24),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    "config2": Configuration(
        time=dc.normal_time_to_utc(2021, 1, 7, 0, 0, 0),
        ra=hms_to_deg(2, 31, 49.09),
        dec=dms_to_deg(89, 15, 50.8),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    "config3": Configuration(
        time=dc.normal_time_to_utc(2020, 12, 23, 7, 34, 34.5),
        ra=hms_to_deg(13, 37, 0.919),
        dec=dms_to_deg(-29, 51, 56.74),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    "m57": Configuration(
        time=dc.normal_time_to_utc(2024, 3, 13, 0, 0, 0),
        ra=hms_to_deg(18, 53, 35.097),
        dec=dms_to_deg(33, 1, 44.88),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

    "veil": Configuration(
        time=dc.normal_time_to_utc(2024, 3, 13, 0, 0, 0),
        ra=hms_to_deg(20, 45, 37.99),
        dec=dms_to_deg(39, 42, 29.9),
        lon=dms_to_deg(10, 53, 22),
        lat=dms_to_deg(49, 53, 6)),

}

# Getter and Setter functions


def load_file(debug_mode=False) -> bool:
    global configurations
    if not debug_mode:
        try:
            configurations = sl.load_from_file()
            return True
        except FileNotFoundError:
            configurations = examples_old
            return False
    else:
        configurations = examples_old
        return True


def save_file(debug_mode=False) -> None:
    if not debug_mode:
        sl.save_to_file(configurations)


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
    current_config.time = dc.normal_time_to_utc(
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

# Data management


def init_values():
    global use_current_time
    use_current_time = True
    set_time(2020, 12, 23, 7, 34, 34.5)
    set_ra(13, 37, 0.919)
    set_dec(-29, 51, 56.74)
    set_lon(10, 53, 22)
    set_lat(49, 53, 6)
    set_lat(49, 53, 6)


def exec_configuration(config_name: str) -> list:
    ex = configurations[config_name]
    time_jd = ex.time.jd
    ra_deg = ex.ra
    dec_deg = ex.dec
    lon_deg = ex.lon
    lat_deg = ex.lat
    [era, az, el] = comp.compute_azimuth_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
    return [era, az, el]


def change_output_mode() -> bool:
    return switch_output_degrees()


def execute() -> list:
    time_jd = get_time_jd()
    ra_deg = get_ra()
    dec_deg = get_dec()
    lon_deg = get_lon()
    lat_deg = get_lat()
    [era, az, el] = comp.compute_azimuth_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
    return [era, az, el]


def reset_time():
    global use_current_time
    use_current_time = True


def reset_location():
    set_lon(10, 53, 22)
    set_lat(49, 53, 6)


def load(config_name: str):
    ex = configurations[config_name]
    set_time_utc(new_time=ex.time)
    set_ra(ex.ra, single_value=True)
    set_dec(ex.dec, single_value=True)
    set_lon(ex.lon, single_value=True)
    set_lat(ex.lat, single_value=True)


def remove_config(config: str):
    configurations.pop(config)


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
        [era, az, el] = comp.compute_azimuth_elevation(time, ra, dec, lon, lat)
        values.append((time, era, az, el))
        time += step_size / 24
    return values


def get_viable_objects(start_time=19, end_time=6, cutoff=2, show_all=True) -> list:
    cur_time: Time = dc.normal_time_to_utc(2024, 3, 13, 0, 0, 0)
    cur_lon: float = dms_to_deg(10, 53, 22)
    cur_lat: float = dms_to_deg(49, 53, 6)
    objects: list = si.get_objects()
    # Stars are roughly visible from 19:00 to 6:00
    result = []
    for (name, ra, dec) in objects:
        ra_deg = hms_to_deg(*ra)
        dec_deg = dms_to_deg(*dec)
        config = Configuration(time=cur_time, ra=ra_deg, dec=dec_deg, lon=cur_lon, lat=cur_lat)
        values = plot_config(config, 24, 0.1)
        max_el = -90
        count_over_30 = 0
        for (time_jd, era, az, el) in values:
            max_el = max(el, max_el)
            hour = dc.hours_from_julian_days(time_jd)
            count_over_30 += el > 30 and (hour > start_time or hour < end_time)
        if count_over_30 > len(values) * (cutoff / 24) or show_all:
            result.append((name, config))

    return result


def search_database_object(objects: list):
    cur_time: Time = dc.normal_time_to_utc(2024, 3, 13, 0, 0, 0)
    cur_lon: float = dms_to_deg(10, 53, 22)
    cur_lat: float = dms_to_deg(49, 53, 6)
    objects: list = si.get_objects(objects)
    result = []
    for (name, ra, dec) in objects:
        ra_deg = hms_to_deg(*ra)
        dec_deg = dms_to_deg(*dec)
        config = Configuration(time=cur_time, ra=ra_deg, dec=dec_deg, lon=cur_lon, lat=cur_lat)
        result.append((name, config))

    return result
