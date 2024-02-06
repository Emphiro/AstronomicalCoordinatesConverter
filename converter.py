import numpy as np
import math
import sys
from astropy.time import Time

#constants
TIME_2000 =  2451545.0
PI2 = 2 * math.pi





# date conversions

def normal_time_to_julian(year, month, day, hour, min , sec):
    """convert time in year-month-day hour:minutes:seconds format to Julian days"""
    return Time("{}-{}-{}T{}:{}:{}".format(year, month, day, hour, min , sec), format="isot", scale="utc").jd

def normal_time_to_utc(year, month, day, hour, min , sec):
    """convert time in year-month-day hour:minutes:seconds format to Time object"""
    return Time("{}-{}-{}T{}:{}:{}".format(year, month, day, hour, min , sec), format="isot", scale="utc")

# angle conversions

def dms_to_deg(deg, min, sec):
    """convert degrees, arcminutes and arcseconds to degrees"""
    sign = -1 if deg < 0 else 1 
    deg = abs(deg)
    return sign * deg + sign * min/60 + sign * sec/(60 ** 2)

def hms_to_deg(hour, min, sec):
    """convert hours, minutes and seconds to degrees"""
    sign = -1 if hour < 0 else 1 
    hour = abs(hour)
    return ((sign * hour + sign*min/60 + sign * sec/(60 ** 2)) / 24) * 360

def angle_to_gmst(theta):
    return 86400 * (theta / PI2)

def deg_to_rad(degrees):
    """convert degrees to radians"""
    return (degrees / 360) * PI2

def rad_to_deg(rad):
    """convert radians to degrees"""
    return (rad / PI2) * 360

def deg_to_dms(degrees):
    """convert degrees to degrees, arcminutes and arcseconds"""
    sign = -1 if degrees < 0 else 1 
    degrees = abs(degrees)
    degs = math.floor(degrees)
    mins = math.floor((degrees-degs) * 60)
    secs = (((degrees-degs) * 60) - mins) * 60 
    return "{}d {}m {:.2f}s".format(sign*degs, mins, secs)

def deg_to_hms(degrees):
    """convert degrees to hours, minutes and seconds"""
    sign = -1 if degrees < 0 else 1 
    degrees = abs(degrees)
    degrees = (degrees / 360) * 24
    degs = math.floor(degrees)
    mins = math.floor((degrees-degs) * 60)
    secs = (((degrees-degs) * 60) - mins) * 60 
    return "{}h {}m {:.2f}s".format(sign*degs, mins, secs)

time = normal_time_to_julian(2020, 12, 23, 7, 34, 34.5)
time_utc = normal_time_to_utc(2020, 12, 23, 7, 34, 34.5)
ra = hms_to_deg(13, 37, 0.919)
dec = dms_to_deg(-29, 51, 56.74)
lon = dms_to_deg(10, 53, 22)
lat = dms_to_deg(49, 53, 6)

# Setter functions

def set_time(year, month, day, hour, min, sec):
    global time_utc
    time_utc = normal_time_to_utc(year, month, day, hour, min, sec)
    global time 
    time = time_utc.jd
    
def set_ra(hours, minutes, seconds):
    global ra
    ra = hms_to_deg(hours, minutes, seconds)

def set_dec(degrees, minutes, seconds):
    global dec
    dec = dms_to_deg(degrees, minutes, seconds)

def set_lon(degrees, minutes, seconds):
    global lon
    lon = dms_to_deg(degrees, minutes, seconds)
    
def set_lat(degrees, minutes, seconds):
    global lat
    lat = dms_to_deg(degrees, minutes, seconds)

# Actual computation

def angle_to_coords(ra, dec):
    """convert spherical coordinates to cartesian coordinates"""
    return np.array([math.cos(ra)*math.cos(dec), math.sin(ra)*math.cos(dec), math.sin(dec)])

def earth_rot_angle(time_jd):
    """compute earth rotation angle (ERA) from time in julian days"""
    du = time_jd - TIME_2000
    angle = PI2 * (0.7790572732640 + 1.00273781191135448 * du)
    return angle

def compute_Rz(theta):
    """compute rotation matrix around z axis using theta in radians"""
    cos = math.cos(theta)
    sin = math.sin(theta)
    return np.array([[cos, sin, 0],[-sin, cos, 0],[0, 0, 1]])

def compute_Rx():
    """compute rotation matrix around x axis"""
    return np.array([[-1, 0, 0],[0, 1, 0],[0, 0, 1]])

def compute_Ry(phi):
    """compute rotation matrix around y axis using latitude in radians"""
    phi = (math.pi / 2) - phi % PI2
    cos = math.cos(phi)
    sin = math.sin(phi)
    return np.array([[cos, 0, -sin],[0, 1, 0],[sin, 0, cos]])

def compute_azimut_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg):
    """compute era, azimut and elevation from time in julian days and right ascension, declination, longitude and latitude in degrees"""
    ra = deg_to_rad(ra_deg) % PI2
    dec = deg_to_rad(dec_deg) % PI2
    lat = deg_to_rad(lat_deg) % PI2
    lon = deg_to_rad(lon_deg) % PI2
    theta = earth_rot_angle(time_jd)
    era = rad_to_deg(theta % PI2)
    theta = (theta + lon) % PI2
    [x, y, z] = compute_Rx() @ compute_Ry(lat) @ compute_Rz(theta) @ angle_to_coords(ra, dec)
   
    el = math.acos(z)
    el = math.pi/2 - el
    az = math.atan(y / x)
    if x < 0:
        az = az + math.pi
    elif x > 0 and y < 0:
       az = az + PI2
    
    az_dms = deg_to_dms(rad_to_deg(az))
    el_dms = deg_to_dms(rad_to_deg(el))
    return [era, az_dms, el_dms]
    

# The Example testcases

class Example:
    def __init__(self, time, ra, dec, lon, lat):
        self.time = time
        self.ra = ra
        self.dec = dec
        self.lon = lon
        self.lat = lat

examples = [
    Example(
        time =normal_time_to_julian(2021, 2, 7, 22, 23, 24),
        ra = hms_to_deg(18, 18, 48), 
        dec = dms_to_deg(-13, 48, 24),
        lon = dms_to_deg(10, 53, 22),
        lat = dms_to_deg(49, 53, 6)),
    
    Example(
        time = normal_time_to_julian(2021, 1, 7, 0, 0, 0),
        ra = hms_to_deg(2, 31, 49.09),
        dec = dms_to_deg(89, 15, 50.8),
        lon = dms_to_deg(10, 53, 22),
        lat = dms_to_deg(49, 53, 6)),
    
    Example(
        time = normal_time_to_julian(2020, 12, 23, 7, 34, 34.5),
        ra = hms_to_deg(13, 37, 0.919),
        dec = dms_to_deg(-29, 51, 56.74),
        lon = dms_to_deg(10, 53, 22),
        lat = dms_to_deg(49, 53, 6))
]


# I/O funcions

def print_solution(era, az, el):
    print("Era: {:.4f}\nAzimut: {}\nElevation: {}".format(era, az, el))

def change_date(inputString):
    inputNum = inputString.split()
    date = [0, 0, 0, 0, 0, 0]
    try:
        if (len(inputNum) > 2 and inputNum[1] == "-v"):

            for [i, value] in enumerate(inputNum[2:]):
                date[i] = int(value) 
        else:
            date[0] = int(input("year? "))
            date[1] = int(input("month? "))
            date[2] = int(input("day? "))
            date[3] = int(input("hour? "))
            date[4] = int(input("minute? "))
            date[5] = float(input("second? "))
    except ValueError:
        print("Invalid Date. Please try again")
        change_date("")
        return
    
    try:
        set_time(date[0], date[1], date[2], date[3], date[4], date[5])
    except ValueError:
        print("Invalid Date. Please try again")
        change_date("")
        return
    print("Time set to {}".format(time_utc))
    
def change_ra(inputString):
    inputNum = inputString.split()
    rasc = [0, 0, 0]
    try:
        if (len(inputNum) > 2 and inputNum[1] == "-v"):

            for [i, value] in enumerate(inputNum[2:]):
                rasc[i] = int(value) 
        else:
            rasc[0] = int(input("hour? "))
            rasc[1] = int(input("minute? "))
            rasc[2] = float(input("second? "))
    except ValueError:
        print("Invalid Value. Please try again")
        change_ra("")
        return
    
    try:
        set_ra(rasc[0], rasc[1], rasc[2])
    except ValueError:
        print("Invalid Value. Please try again")
        change_ra("")
        return
    print("Right Ascension set to {}".format(deg_to_hms(ra)))
    
def change_dec(inputString):
    inputNum = inputString.split()
    decl = [0, 0, 0]
    try:
        if (len(inputNum) > 2 and inputNum[1] == "-v"):

            for [i, value] in enumerate(inputNum[2:]):
                decl[i] = int(value) 
        else:
            decl[0] = int(input("degree? "))
            decl[1] = int(input("arcminutes? "))
            decl[2] = float(input("arcseconds? "))
    except ValueError:
        print("Invalid Value. Please try again")
        change_dec("")
        return
    
    try:
        set_dec(decl[0], decl[1], decl[2])
    except ValueError:
        print("Invalid Value. Please try again")
        change_dec("")
        return
    print("Declination set to {}".format(deg_to_dms(dec)))
    
def change_lon(inputString):
    inputNum = inputString.split()
    long = [0, 0, 0]
    try:
        if (len(inputNum) > 2 and inputNum[1] == "-v"):

            for [i, value] in enumerate(inputNum[2:]):
                long[i] = int(value) 
        else:
            long[0] = int(input("degree? "))
            long[1] = int(input("arcminutes? "))
            long[2] = float(input("arcseconds? "))
    except ValueError:
        print("Invalid Value. Please try again")
        change_lon("")
        return
    
    try:
        set_lon(long[0], long[1], long[2])
    except ValueError:
        print("Invalid Value. Please try again")
        change_lon("")
        return
    print("Longitude set to {}".format(deg_to_dms(lon)))
    
def change_lat(inputString):
    inputNum = inputString.split()
    lati = [0, 0, 0]
    try:
        if (len(inputNum) > 2 and inputNum[1] == "-v"):

            for [i, value] in enumerate(inputNum[2:]):
                lati[i] = int(value) 
        else:
            lati[0] = int(input("degree? "))
            lati[1] = int(input("arcminutes? "))
            lati[2] = float(input("arcseconds? "))
    except ValueError:
        print("Invalid Value. Please try again")
        change_lat("")
        return
    
    try:
        set_lat(lati[0], lati[1], lati[2])
    except ValueError:
        print("Invalid Value. Please try again")
        change_lat("")
        return
    print("Latitude set to {}".format(deg_to_dms(lat)))

def reset_location(inputString):
    set_lon(10, 53, 22)
    set_lat(49, 53, 6)

def reset_time(inputString):
    set_time(2024, 2, 6, 7, 34, 34.5)
    
def list_values(inputString):
    print("Time set to {}".format(time_utc))
    print("Right Ascension set to {}".format(deg_to_hms(ra)))
    print("Declination set to {}".format(deg_to_dms(dec)))
    print("Longitude set to {}".format(deg_to_dms(lon)))
    print("Latitude set to {}".format(deg_to_dms(lat)))

def execute(inputString):
    if(len(inputString.split()) > 1):
        print_example(inputString.split()[1])
        return
    time_jd = time
    ra_deg = ra
    dec_deg = dec
    lon_deg = lon
    lat_deg = lat
    [era, az, el] = compute_azimut_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
    print_solution(era, az, el)

def not_available(inputString):
    print("Someone has not yet implemented this function :(")

def print_example(num):
    """prints the example specified by the integer num"""
    if num is None:
        num = input("Which example? ")
    try:
        num = int(num) - 1
    except ValueError:
        print("Please specify an example between 1 and 3")
    if num < len(examples) and num >= 0:
        ex = examples[num]
        time_jd = ex.time
        ra_deg = ex.ra
        dec_deg = ex.dec
        lon_deg = ex.lon
        lat_deg = ex.lat
        [era, az, el] = compute_azimut_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
        print_solution(era, az, el)
    else:
        print("Please specify an example between 1 and 3")
    
def print_help(inputString):
    print("Available commands:")
    for [command, description] in available_commands.items():
        print(command + ":")
        print(description)

available_commands = {
    "cdate": "Change the date",
    "cra": "Change the right ascension",
    "cdec": "Change the declination",
    "clon": "Change the longitude",
    "clat": "Change the latitude",
    "rloc": "Change the location to remeis Observatorium",
    "rdate": "Change the time to the current time",
    "ex": "Calculate the Era, Azimut and Elevation for the currently set values",
    "ls": "Show the currently set values"
}

executable_commands = {
    "help" : print_help,
    "cdate": change_date,
    "cra": change_ra,
    "cdec": change_dec,
    "clon": change_lon,
    "clat": change_lat,
    "rloc": reset_location,
    "rdate": reset_time,
    "ex": execute,
    "ls": list_values
}

def inputloop():
    inputString = input()
    if len(inputString) == 0:
        return
    command = executable_commands[inputString.split()[0]]
    if command is None:
        print("No matching command found. Type help for a list of commands")
    else:
        command(inputString)
    
def main():
    if(len(sys.argv) > 1):
        arg = sys.argv[1]
        if (arg == "-e"):
            print_example((sys.argv[2] if len(sys.argv) > 2 else None))
            return
        if (arg == "-h"):
            print_help("")
            return
   
    
    print("Welcome to this coordinates converter program!")
    print()
    print("Type help for a list of commands")
    while 1:
        try:
            inputloop()
        except EOFError:
            return
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    main()
