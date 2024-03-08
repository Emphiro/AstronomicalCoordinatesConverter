#!/usr/bin/env python3
from converter_io import terminal_input as ti
from astronomical_data import config_management as cm

import math
import sys


# constants

TIME_2000: float = 2451545.0
PI2: float = 2 * math.pi
DEBUG_MODE: bool = False


# Global Variables (set in init_values)


def main():
    global DEBUG_MODE
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "-e":
            ti.exec_configuration_input((sys.argv[2] if len(sys.argv) > 2 else None))
            return
        if arg == "-h":
            ti.print_help_input(None)
            return
        if arg == "-d":
            DEBUG_MODE = True
    cm.init_values()

    if not cm.load_file(debug_mode=DEBUG_MODE):
        print("No file was found. Loading basic configurations", file=sys.stderr)

    print("Welcome to this coordinates converter program!")
    print()
    print("Type help for a list of commands")
    while 1:
        try:
            ti.input_loop()
        except EOFError:
            break
        except KeyboardInterrupt:
            break
    cm.save_file(debug_mode=DEBUG_MODE)


if __name__ == "__main__":
    main()
