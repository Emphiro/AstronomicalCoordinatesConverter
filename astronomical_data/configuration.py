from dataclasses import dataclass

from astropy.time import Time

from utils import angle_converter as ac

current_configuration = None

class Configuration:
    def __init__(self, time, ra, dec, lon, lat):
        self.time: Time = time
        time
        self.ra: float = ra
        self.dec: float = dec
        self.lon: float = lon
        self.lat: float = lat

    def __str__(self):
        return (f"Time: {self.time}\nRight Ascension: {ac.deg_to_hms(self.ra)}\n"
                f"Declination: {ac.deg_to_dms(self.dec)}\nLongitude: {ac.deg_to_dms(self.lon)}"
                f"\nLatitude: {ac.deg_to_dms(self.lat)}")

    def get_time(self) -> Time:
        return self.time

    def get_ra(self) -> float:
        return self.ra

    def get_dec(self) -> float:
        return self.dec

    def get_lon(self) -> float:
        return self.lon

    def get_lat(self) -> float:
        return self.lat

@dataclass
class Location:
    longitude: float
    latitude: float


@dataclass
class AstronomicalObject:
    right_ascension: float
    declination: float
