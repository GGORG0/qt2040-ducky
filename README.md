# QT2040-Ducky

A USB Rubber Ducky interpreter for the [Adafruit Trinkey QT2040](https://www.adafruit.com/product/5056) using CircuitPython.

## Installation

1. [Install CircuitPython](https://learn.adafruit.com/adafruit-trinkey-qt2040/circuitpython)
2. [Install the `adafruit_hid`, `adafruit_pixelbuf`, `neopixel` libraries from the official library bundle](https://learn.adafruit.com/adafruit-trinkey-qt2040/circuitpython-libraries#downloading-the-adafruit-circuitpython-library-bundle-2977982)
3. Copy the `boot.py`, `code.py` and `commands.py` files to the `CIRCUITPY` drive
4. Put a `payload.dd` Ducky Script file on the drive. Be careful, as it will probably be executed right away! Read below to see how to prevent that.

## Usage

Read [pico-ducky's README](https://github.com/dbisu/pico-ducky#readme), as this project is based on it.
I just adapted it to work with the QT2040.

### Safe Mode

To prevent both accidental self-attacks and to increase stealth, the `boot.py` script disables the `CIRCUITPY` drive functionality.

To be able to change the files on the flash storage, enter [Safe Mode](https://learn.adafruit.com/adafruit-trinkey-qt2040/circuitpython#safe-mode-3097754).
It will not run any code and will enable the USB drive functionality!
