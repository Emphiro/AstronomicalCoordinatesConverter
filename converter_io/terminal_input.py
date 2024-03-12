import converter as conv
from astronomical_data import config_management as cm
from utils import angle_converter as ac
from utils import date_converter as dc
from converter_io import plotting
import textwrap

from astropy.time import Time


def parse_y_n(input_string: str) -> bool:
    """return True if the input is y or Y else false"""
    return input_string.lower() == "y"


def not_available_input(input_string: None):
    print("Someone has not yet implemented this function :(")


def exec_configuration_input(config_name: str):
    """prints the configuration specified by the string config_name"""
    if config_name is None:
        config_name = input("Which configuration? ")

    if config_name in cm.configurations:
        [era, az, el] = cm.exec_configuration(config_name)
        print_solution(era, az, el)
    else:
        print("Please specify an existing configuration")


def print_help_input(input_string: None):
    print("Available commands:")
    for [command, description] in available_commands.items():
        print(command + ":")
        usage_str = "Usage: " + usage[command]
        print(textwrap.indent(usage_str, "       "))
        print(textwrap.indent(description, "    "))


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


def change_output_mode_input(input_string: None):
    cm.change_output_mode()
    output = "Output will be given in degrees" if cm.output_degrees else \
        "Output will be given in degrees arc-minutes and arc-seconds"
    print(output)


def execute_input(input_string: str):
    if len(input_string.split()) > 1:
        exec_configuration_input(" ".join(input_string.split()[1:]))
        return
    [era, az, el] = cm.execute()
    print_solution(era, az, el)


def list_configurations_input(input_string: None):
    list_configurations()


def list_configurations():
    for (name, config) in cm.configurations.items():
        print("Configuration {}:".format(name))
        print(textwrap.indent(str(config), "    "))


def list_values():
    print("Time set to {}".format(cm.get_time()))
    print("Right Ascension set to {}".format(ac.deg_to_hms(cm.get_ra())))
    print("Declination set to {}".format(ac.deg_to_dms(cm.get_dec())))
    print("Longitude set to {}".format(ac.deg_to_dms(cm.get_lon())))
    print("Latitude set to {}".format(ac.deg_to_dms(cm.get_lat())))


def list_values_input(input_string: None):
    list_values()


def reset_time_input(input_string: None):
    cm.reset_time()
    print("set Time to current time")


def reset_location_input(input_string: None):
    cm.reset_location()
    print("set Location to remeis observatory")


def change_value_input(input_string: str):
    types = {
        "clat": [cm.set_lat, "dms", "Latitude"],
        "clon": [cm.set_lon, "dms", "Longitude"],
        "cdec": [cm.set_dec, "dms", "Declination"],
        "cra": [cm.set_ra, "hms", "Right Ascension"],
        "ctime": [cm.set_time, "time", "Time"]
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


def print_solution(era: float, az: float, el: float):
    print("Era: {:.4f}\nAzimuth: {}\nElevation: {}".format(
        era, ac.deg_to_dms(az), ac.deg_to_dms(el)))


def load_input(input_string: str):
    """loads a configuration to be the currently used value"""
    config_name = " ".join(input_string.split()[1:]) if len(input_string.split()) > 1 else None
    if config_name is None:
        config_name = input("Which configuration? ")

    if config_name in cm.configurations:
        cm.load(config_name)
    else:
        print("Please specify an existing configuration name")
        return
    print(config_name)
    list_values()


def remove_config_input(input_string: str):
    """removes a configuration from the array"""
    config_name = " ".join(input_string.split()[1:]) if len(input_string.split()) > 1 else None
    if config_name is None:
        config_name = input("Which configuration? ")

    if config_name in cm.configurations:
        confirmation: str = input("Are you sure you want to delete configuration {}? (y/n) ".
                                  format(config_name))
        if parse_y_n(confirmation):
            cm.remove_config(config_name)
        else:
            return
    else:
        print("Please specify an existing configuration name")
        return
    print("Successfully removed the specified configuration")


def add_config_input(input_string: str):
    input_array = input_string.split()
    if len(input_array) > 1:
        config_name = " ".join(input_string.split()[1:])
        name = cm.add_config(config_name)
    else:
        name = cm.add_config()

    if name is not None:
        print("Saved as Configuration \"{}\"".format(name))
    else:
        print("There is already a configuration named \"{}\"".format(input_array[1]))


def plot_input(input_string: str):
    input_array = input_string.split("\"")
    config_name = None
    if len(input_array) == 3:
        config_name = input_array[1]
        input_string = " ".join([input_array[0], "name", input_array[2]])

    input_array = input_string.split()

    name: str = input_array[0]
    is_verbose = "-v" in input_array
    is_polar = "-p" in input_array
    save_plot = "-s" in input_array
    draw_lines: bool = "-l" in input_array
    if len(input_array) < 2:
        print("not enough arguments")
        print("Usage: " + usage[name])
        return
    if config_name is None:
        config_name = input_array[1]
    try:
        adjusted_len = len(input_array) - is_verbose - draw_lines - is_polar - save_plot
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
    if config_name not in cm.configurations:
        print(f"{config_name} is not a saved configuration")
        return
    print(f"step_size {step_size}, config name: {config_name}, end: {end}")
    print(f"ra: {cm.configurations[config_name].ra} dec: {cm.configurations[config_name].dec}")
    values = cm.plot_config(cm.configurations[config_name], end, step_size)
    if is_verbose:
        print_plot(values)
    if is_polar:
        plotting.show_polar_plot(values, config_name, draw_lines)
    else:
        plotting.show_simple_plot(values, config_name)


def print_plot(values: list):
    for (i, (time, era, az, el)) in enumerate(values):
        time_utc: Time = Time(time, format="jd")
        time_utc.format = "iso"
        print(f"{i} {time_utc}:")
        print(f"{dc.hours_from_julian_days(time)}")
        print_solution(era, az, el)


def input_get_viable_objects(input_string: None):
    print("Fetching data. This may take some time...")
    objects = cm.get_viable_objects()
    for (name, config) in objects:
        print(f"Name: {name}")
        user_input: str = input("Show plot (y/n) ")
        show_plot: bool = parse_y_n(user_input)
        if show_plot:
            print(f"ra: {config.ra} dec: {config.dec}")
            values = cm.plot_config(config, 24, 1)
            print_plot(values)
            plotting.show_simple_plot(values, name, detailed=True)


def input_search_viable_objects(input_string: str):
    object_name = input_string.split()[1]
    print("Fetching data. This may take some time...")
    objects = cm.search_database_object([object_name])
    if objects is None:
        print(f"No objects with name {object_name} found")
    for (name, config) in objects:
        values = cm.plot_config(config, 24, 1)
        print_plot(values)
        plotting.show_simple_plot(values, name, detailed=True)


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
            "\n  -p: Draw a polar plot instead of the normal plot"
            "\n  -v: All the calculated values will be printed to the console"
            "\n  -l: Draw lines between the calculated values",
    "av": "Gets all the viable objects for observation",
    "sr": "Search for object on the simbad database and plot the result",
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
    "plot": "plot config_name:str [length:float] [time_step: float] [-p] [-v] [-d]",
    "av": "av",
    "sr": "sr name:str",
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
    "av": input_get_viable_objects,
    "sr": input_search_viable_objects,
}