import re
import time

import board
import digitalio
import neopixel
import supervisor
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

from commands import duckyCommands

variables = {}
functions = {}

button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

pixel.fill((0, 255, 0))

time.sleep(0.5)
supervisor.runtime.autoreload = False

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

defaultDelay = 0

pixel.fill((255, 255, 0))


def convertLine(line):
    newline = []
    for key in filter(None, line.split(" ")):
        key = key.upper()
        command_keycode = duckyCommands.get(key, None)
        if command_keycode is not None:
            newline.append(command_keycode)
        elif hasattr(Keycode, key):
            newline.append(getattr(Keycode, key))
        else:
            print(f"Unknown key: {key}")
    return newline


def runScriptLine(line):
    if isinstance(line, str):
        line = convertLine(line)
    pixel.fill((255, 0, 0))
    for k in line:
        kbd.press(k)
    kbd.release_all()
    pixel.fill((255, 255, 0))


def sendString(line):
    pixel.fill((255, 0, 0))
    layout.write(line)
    pixel.fill((255, 255, 0))


def parseLine(line, script_lines):
    global defaultDelay, variables, functions
    line = line.strip()
    if line[0:3] == "REM":
        pass
    elif line[0:5] == "DELAY":
        time.sleep(float(line[6:]) / 1000)
    elif line[0:6] == "STRING":
        sendString(line[7:])
    elif line[0:5] == "PRINT":
        print("[SCRIPT]: " + line[6:])
    elif line[0:6] == "IMPORT":
        runScript(line[7:])
    elif line[0:13] == "DEFAULT_DELAY":
        defaultDelay = int(line[14:]) * 10
    elif line[0:12] == "DEFAULTDELAY":
        defaultDelay = int(line[13:]) * 10
    elif line[0:3] == "LED":
        _, r_val, g_val, b_val = line.split()
        pixel.fill((int(r_val), int(g_val), int(b_val)))
    elif line[0:21] == "WAIT_FOR_BUTTON_PRESS":
        while not button.value:
            pass
    elif line.startswith("VAR"):
        _, var, _, value = line.split()
        variables[var] = int(value)
    elif line.startswith("FUNCTION"):
        func_name = line.split()[1]
        functions[func_name] = []
        line = next(script_lines).strip()
        while line != "END_FUNCTION":
            functions[func_name].append(line)
            line = next(script_lines).strip()
    elif line.startswith("WHILE"):
        condition = re.search(r"\((.*?)\)", line).group(1)
        var_name, _, condition_value = condition.split()
        condition_value = int(condition_value)
        loop_code = []
        line = next(script_lines).strip()
        while line != "END_WHILE":
            if not (line.startswith("WHILE")):
                loop_code.append(line)
            line = next(script_lines).strip()
        while variables[var_name] > condition_value:
            for loop_line in loop_code:
                parseLine(loop_line, {})
            variables[var_name] -= 1
    elif line in functions:
        updated_lines = []
        inside_while_block = False
        for func_line in functions[line]:
            if func_line.startswith("WHILE"):
                inside_while_block = True
                updated_lines.append(func_line)
            elif func_line.startswith("END_WHILE"):
                inside_while_block = False
                updated_lines.append(func_line)
                parseLine(updated_lines[0], iter(updated_lines))
                updated_lines = []
            elif inside_while_block:
                updated_lines.append(func_line)
            elif not (
                func_line.startswith("END_WHILE") or func_line.startswith("WHILE")
            ):
                parseLine(func_line, iter(functions[line]))
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)


def runScript(file):
    global defaultDelay

    print(f"running: {file}")
    try:
        with open(file, "r", encoding="utf-8") as f:
            script_lines = iter(f.readlines())
            previousLine = ""
            for line in script_lines:
                print(f"=> {line}")

                if line[0:6] == "REPEAT":
                    for i in range(int(line[7:])):
                        parseLine(previousLine, script_lines)
                        time.sleep(float(defaultDelay) / 1000)
                else:
                    parseLine(line, script_lines)
                    previousLine = line
                time.sleep(float(defaultDelay) / 1000)
    except OSError:
        print("Unable to open file", file)


runScript("payload.dd")

print("*** FINISHED ***")

while True:
    for i in range(256):
        pixel.fill((0, i, 0))
        time.sleep(0.001)
    for i in range(256):
        pixel.fill((0, 255 - i, 0))
        time.sleep(0.001)
