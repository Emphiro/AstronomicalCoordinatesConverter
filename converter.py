import numpy as np
import math
import sys
from astropy.time import Time
from astropy.coordinates import Angle
#time = Time("1890-08-20T00:00:00.000", format="isot", scale="utc")
#time_jd = time.jd
TIME_2000 =  2451545.0
PI2 = 2 * math.pi



available_commands = {
    "cdate": "Change the date",
    "cra": "Change the right ascension",
    "cdec": "Change the declination",
    "clon": "Change the longitude",
    "clan": "Change the lattitude",
    "rloc": "Change the location to remeis Observatorium",
    "rtime": "Change the time to the current time",
    "ex": "Calculate the Era, Azimut and Elevation for the currently set values",
    "ls": "Show the currently set values"
}

def normal_time_to_julian(year, month, day, hour, min , sec):
    return Time("{}-{}-{}T{}:{}:{}".format(year, month, day, hour, min , sec), format="isot", scale="utc").jd

def normal_time_to_utc(year, month, day, hour, min , sec):
    return Time("{}-{}-{}T{}:{}:{}".format(year, month, day, hour, min , sec), format="isot", scale="utc")


def dms_to_deg(deg, min, sec):
    sign = -1 if deg < 0 else 1 
    deg = abs(deg)
    return sign * deg + sign * min/60 + sign * sec/(60 ** 2)

def hms_to_deg(hour, min, sec):
    sign = -1 if hour < 0 else 1 
    hour = abs(hour)
    return ((sign * hour + sign*min/60 + sign * sec/(60 ** 2)) / 24) * 360

def angle_to_gmst(theta):
    return 86400 * (theta / PI2)

def deg_to_rad(degrees):
    return (degrees / 360) * PI2

def rad_to_deg(rad):
    return (rad / PI2) * 360

def deg_to_dms(degrees):
    sign = -1 if degrees < 0 else 1 
    degrees = abs(degrees)
    degs = math.floor(degrees)
    mins = math.floor((degrees-degs) * 60)
    secs = (((degrees-degs) * 60) - mins) * 60 
    return "{}d {}m {}s".format(sign*degs, mins, secs)

def deg_to_hms(degrees):
    sign = -1 if degrees < 0 else 1 
    degrees = abs(degrees)
    degrees = (degrees / 360) * 24
    degs = math.floor(degrees)
    mins = math.floor((degrees-degs) * 60)
    secs = (((degrees-degs) * 60) - mins) * 60 
    return "{}h {}m {}s".format(sign*degs, mins, secs)

time = normal_time_to_julian(2020, 12, 23, 7, 34, 34.5)
time_utc = normal_time_to_utc(2020, 12, 23, 7, 34, 34.5)
ra = hms_to_deg(13, 37, 0.919)
dec = dms_to_deg(-29, 51, 56.74)
lon = dms_to_deg(10, 53, 22)
lat = dms_to_deg(49, 53, 6)


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

def earth_rot_angle(time_jd):
    du = time_jd - TIME_2000
    angle = PI2 * (0.7790572732640 + 1.00273781191135448 * du)
    return angle

def angle_to_coords(ra, dec):
    return np.array([math.cos(ra)*math.cos(dec), math.sin(ra)*math.cos(dec), math.sin(dec)])

def compute_Rz(theta):
    cos = math.cos(theta)
    sin = math.sin(theta)
    return np.array([[cos, sin, 0],[-sin, cos, 0],[0, 0, 1]])

def compute_Rx():
    return np.array([[-1, 0, 0],[0, 1, 0],[0, 0, 1]])

def compute_Ry(phi):
    phi = (math.pi / 2) - phi % PI2
    cos = math.cos(phi)
    sin = math.sin(phi)
    return np.array([[cos, 0, -sin],[0, 1, 0],[sin, 0, cos]])

def compute_azimut_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg):
    ra = deg_to_rad(ra_deg) % PI2
    dec = deg_to_rad(dec_deg) % PI2
    lat = deg_to_rad(lat_deg) % PI2
    lon = deg_to_rad(lon_deg) % PI2
    theta = earth_rot_angle(time_jd)
    era = rad_to_deg(theta % PI2)
    #print(era)
    theta = (theta + lon) % PI2
    [x, y, z] = compute_Rx() @ compute_Ry(lat) @ compute_Rz(theta) @ angle_to_coords(ra, dec)
   
    el = math.acos(z)
    el = math.pi/2 - el
    az = math.atan(y / x)
    if x < 0:
        az = az + math.pi
    elif x > 0 and y < 0:
       az = az + PI2
    
    #az = az + math.pi
    #print(deg_to_hms(rad_to_deg(ra)))
    #print(deg_to_dms(rad_to_deg(dec)))
    #print(deg_to_dms(rad_to_deg(lat)))
    #print("{}:{}:{}".format(x, y, z))
    #print(deg_to_dms(rad_to_deg(az)))
    #print(deg_to_dms(rad_to_deg(el)))
    return [era, deg_to_dms(rad_to_deg(az)), deg_to_dms(rad_to_deg(el))]
    
def test1():
    print("Test1")
    time = normal_time_to_julian(2021, 2, 7, 22, 23, 24)
    ra = hms_to_deg(18, 18, 48)
    dec = dms_to_deg(-13, 48, 24)
    lon = dms_to_deg(10, 53, 22)
    lat = dms_to_deg(49, 53, 6)
    [era, az, el] = compute_azimut_elevation(time, ra, dec, lon, lat)
    print("Era: {} \nAzimut: {} \nElevation {}".format(era, az, el))

def test2():
    print("Test2")
    time = normal_time_to_julian(2021, 1, 7, 0, 0, 0)
    ra = hms_to_deg(2, 31, 49.09)
    dec = dms_to_deg(89, 15, 50.8)
    lon = dms_to_deg(10, 53, 22)
    lat = dms_to_deg(49, 53, 6)
    [era, az, el] = compute_azimut_elevation(time, ra, dec, lon, lat)
    print("Era: {} \nAzimut: {} \nElevation {}".format(era, az, el))

def test3():
    print("Test3")
    time = normal_time_to_julian(2020, 12, 23, 7, 34, 34.5)
    ra = hms_to_deg(13, 37, 0.919)
    dec = dms_to_deg(-29, 51, 56.74)
    lon = dms_to_deg(10, 53, 22)
    lat = dms_to_deg(49, 53, 6)
    [era, az, el] = compute_azimut_elevation(time, ra, dec, lon, lat)
    print("Era: {} \nAzimut: {} \nElevation {}".format(era, az, el))


def change_date(inputString):
    inputNum = inputString.split()
    date = [0, 0, 0, 0, 0, 0]
    try:
        if (len(inputNum) > 2 and inputNum[1] == "-d"):

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

def execute(inputString):
    time_jd = time
    ra_deg = ra
    dec_deg = dec
    lon_deg = lon
    lat_deg = lat
    [era, az, el] = compute_azimut_elevation(time_jd, ra_deg, dec_deg, lon_deg, lat_deg)
    print("Era: {} \nAzimut: {} \nElevation {}".format(era, az, el))
    
def print_example(inputString):
    num = sys.argv[2] if len(sys.argv) > 2 else ""
    if(num == ""):
        num = input("Which example? ")
    if(num == "1"):
        test1()
    elif(num == "2"):
        test2()
    elif(num == "3"):
        test3()
    else:
        print("Please specify an example between 1 and 3")
    
def print_help(inputString):
    print("Available commands:")
    for [command, description] in available_commands.items():
        print(command + ":")
        print(description)

executable_commands = {
    "help" : print_help,
    "cdate": change_date,
    "cra": "Change the right ascension",
    "cdec": "Change the declination",
    "clon": "Change the longitude",
    "clan": "Change the lattitude",
    "rloc": "Change the location to remeis Observatorium",
    "rtime": "Change the time to the current time",
    "ex": execute,
    "ls": "Show the currently set values"
}
def inputloop():
    inputString = input()
    #print("!" +inputString)
    command = executable_commands[inputString.split()[0]]
    if command is None:
        print("No matching command found. Type help for a list of commands")
    else:
        command(inputString)
    
def main():
    #print(normal_time_to_julian(1890, 8, 20, 0, 0, 0))
    if(len(sys.argv) > 1):
        arg = sys.argv[1]
        if (arg == "-e"):
            print_example("")
            return
        if (arg == "-h"):
            print_help("")
            return
   
    
    print("Welcome to this shitty program")
    print("Type help for a list of commands")
    while 1:
        try:
            inputloop()
        except EOFError:
            return


if __name__ == "__main__":
    main()
