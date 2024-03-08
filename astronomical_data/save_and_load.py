from astronomical_data.configuration import Configuration
from utils import date_converter as dc
import pickle


def save_to_file(configurations):
    with open('configurations.pkl', 'wb') as outp:
        pickle.dump(configurations, outp, 0)


def load_from_file():
    config: Configuration = Configuration(
        time=dc.normal_time_to_utc(2024, 3, 13, 0, 0, 0),
        ra=18,
        dec=33,
        lon=11,
        lat=50)
    with open('configurations.pkl', 'rb') as inp:
        configurations = pickle.load(inp)
        return configurations
