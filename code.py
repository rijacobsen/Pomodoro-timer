### Pomodoro timer on QTPY2040 with mini OLED
# Written by Horst Obenhaus with input from Ragnhild Jacobsen and Phil
# 2021

from time import sleep, monotonic, monotonic_ns
import board
import terminalio
from collections import OrderedDict
import neopixel
import busio
import digitalio

import displayio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from adafruit_progressbar.horizontalprogressbar import (
    HorizontalProgressBar,
    HorizontalFillDirection,
)


displayio.release_displays()

# Instantiate I2C display
i2c = busio.I2C(board.SCL1, board.SDA1)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)

# Instantiate neopixel LED
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

# Display stuff
WIDTH = 128
HEIGHT = 64

display = adafruit_displayio_ssd1306.SSD1306(
    display_bus, width=WIDTH, height=HEIGHT, auto_refresh=True
)


# Progress bar things
splash = displayio.Group(max_size=10)
display.show(splash)

# set progress bar width and height relative to board's display
x = 0
y = 20
pb_width = WIDTH
pb_height = 40

# Create a new progress_bar object at (x, y)
progress_bar = HorizontalProgressBar(
    (x, y), (pb_width, pb_height), direction=HorizontalFillDirection.LEFT_TO_RIGHT
)

# Append progress_bar to the splash group
splash.append(progress_bar)

# Create a text field above the progress bar
text = "Initialising..."
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=8)
splash.append(text_area)


# Button things
Bbutton = digitalio.DigitalInOut(board.BUTTON)
Bbutton.direction = digitalio.Direction.INPUT
Bbutton_state = Bbutton.value

execute = True

def read_button():
    '''
    Read button state and decide whether or not to "execute"

    '''
    global execute
    Bbutton_state = Bbutton.value
    if not Bbutton_state:
        print('Button pressed')
        execute = not execute
        sleep(.1)


def display_dur_progress(duration, info=""):
    '''
    Display the progress bar progress

    '''
    global execute
    to_ns = 1_000_000_000  # nanoseconds

    start_time = monotonic_ns()  # Initialisation
    diff_time = 0
    while diff_time < duration * to_ns:
        read_button()
        if execute:
            progress_value = progress_bar.maximum * (diff_time / (duration * to_ns))
            if progress_value > 100:
                progress_value = 100

            progress_bar.value = progress_value
            text_area.text = "{}: {:.1f}%".format(info, progress_value)

            cycle_time = monotonic_ns()
            diff_time = cycle_time - start_time
            #print('{} seconds'.format(diff_time/to_ns)) #Use to check precision using 'Serial' in Mu

        else:
            text_area.text = "Paused"

    # At the end: Reset progress bar to 0
    progress_bar.value = progress_bar.minimum


def run_pomodoro():
    '''
    Run a timer with the timings listed below

    '''

    print('Running pomodoro ... ')
    pm_time = 25
    pm_break = 5
    pm_longbreak = 15

    #######################################################
    pm_time *= 60  # seconds
    pm_break *= 60  # seconds
    pm_longbreak *= 60  # seconds

    pomodoro_cycle = OrderedDict(
        [
            ("FOCUS! (1/4)", pm_time),
            ("FIRST BREAK", pm_break),
            ("FOCUS! (2/4)", pm_time),
            ("SECOND BREAK", pm_break),
            ("FOCUS! (3/4)", pm_time),
            ("THIRD BREAK", pm_break),
            ("FOCUS! (4/4)", pm_time),
            ("LONG BREAK", pm_longbreak),
        ]
    )

    for info, duration in pomodoro_cycle.items():
        if "LONG" in info:
            # Set neopixel to green
            current_neopixel_val = (0, 0, 50)
            pixels[0] = current_neopixel_val
            pixels.show()
        elif "BREAK" in info:
            current_neopixel_val = (0, 50, 0)
            pixels[0] = current_neopixel_val
            pixels.show()
        else:
            current_neopixel_val = (50, 25, 0)
            pixels[0] = current_neopixel_val
            pixels.show()

        display_dur_progress(duration, info=info)


if __name__ == '__main__':
    current_time = monotonic()
    print(current_time)
    while True:
        run_pomodoro()








