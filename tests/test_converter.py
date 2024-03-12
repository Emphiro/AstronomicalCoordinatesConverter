from converter_io import terminal_input as ti

import subprocess
import time


EPSILON = 1e-3


def equals(value1, value2):
    return value2 - EPSILON <= value1 <= value2 + EPSILON


def write(p, line):
    assert p.poll() is None, "Program terminated early"
    p.stdin.write(line + "\n")
    p.stdin.flush()


def read(p):
    assert p.poll() is None, "Program terminated early"
    line = p.stdout.readline()
    return line


def test_io():
    for [command_name, function] in ti.executable_commands.items():
        with subprocess.Popen(
                "python3 converter.py -d",
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                universal_newlines=True,
        ) as p:

            num_lines = 3
            # Not working
            for i in range(num_lines):
                line = p.stdout.readline()
                #print(line)
            if command_name == "ctime":
                write(p, f"{command_name} 2022 10 10")
            elif command_name == "rm":
                write(p, f"{command_name} 1")
                write(p, "y")
            else:
                write(p, f"{command_name} 10")
            #print(command_name)
            line = read(p)
            #print(line)
            assert (line != ""), "Read empty line or closed output pipe"

            time.sleep(0.1)
            assert p.poll() is None, "Program terminated early"
            # write(p, "help")
            p.stdin.close()


test_io()
