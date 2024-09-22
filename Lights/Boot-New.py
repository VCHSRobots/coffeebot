from machine import Pin
import time
from neopixel import NeoPixel
import random
import math
import sys
import uselect

NUM_Led = int(16)
led = Pin(25, Pin.OUT)
neopin = Pin(16, Pin.OUT)
np = NeoPixel(neopin, NUM_Led)

def clear():
    for i in range(NUM_Led):
        np[i] = (0, 0, 0)
    np.write()

def setallpix(color):
    for i in range(NUM_Led):
        np[i] = color
    np.write()

def adjust_brightness(color, brightness):
    r, g, b = color
    r = int(r * brightness)
    g = int(g * brightness)
    b = int(b * brightness)
    return (r, g, b)

def fade(color):
    for brightness in [x*0.01 for x in range(101)] + [x*0.01 for x in range(100, -1, -1)]:
        setallpix(adjust_brightness(color,brightness))
        np.write()
        time.sleep(0.01)

Colors3 = {
    "red": (255, 0, 0),
    "orange": (255, 127, 0),
    "yellow": (255, 255, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "indigo": (75, 0, 130),
    "violet": (143, 0, 255)
}

def handle_command(command):
    command = command.strip().lower()
    print(f"Received command: {command}")
    if command == b"red":
        setallpix(Colors3["red"])
        print("Set color to red")
    elif command == b"green":
        setallpix(Colors3["green"])
        print("Set color to green")
    elif command == b"blue":
        setallpix(Colors3["blue"])
        print("Set color to blue")
    elif command == b"clear":
        clear()
        print("Cleared all LEDs")
    else:
        print(f"Unknown command: {command}")

print("Starting LED control program...")
clear()  # Start with all LEDs off

print("LED control program is running. Waiting for commands...")

# Set up poll for stdin
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

while True:
    if poll.poll(0):  # Check if there's data available to read
        try:
            command = sys.stdin.readline().strip()
            if command:
                handle_command(command)
            else:
                print("Received empty command")
        except Exception as e:
            print(f"Error processing command: {e}")