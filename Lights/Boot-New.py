from machine import Pin, UART
import time
from neopixel import NeoPixel
import random

NUM_Led = int(16)
led = Pin(25, Pin.OUT)
neopin = Pin(16, Pin.OUT)
np = NeoPixel(neopin, NUM_Led)

# UART setup
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

def clear():
    for i in range(NUM_Led):
        np[i] = (0, 0, 0)
    np.write()

def setallpix(color):
    for i in range(NUM_Led):
        np[i] = color
    np.write()

Colors3 = [
    (255, 87, 51),   # Coral Red 0
    (64, 224, 208),  # Turquoise 1
    (255, 195, 0),   # Golden Yellow 2
    (75, 0, 130),    # Indigo 3
    (50, 205, 50),   # Lime Green 4
    (255, 105, 180), # Hot Pink 5
    (0, 128, 128),   # Teal 6
    (255, 165, 0),   # Orange 7
    (138, 43, 226),  # Blue Violet 8
    (0, 191, 255),   # Deep Sky Blue 9
]

def handle_command(command):
    command = command.strip().lower()
    print(f"Received command: {command}")
    if command == b"red":
        setallpix(Colors3[2])
        print("Set color to red")
    elif command == b"green":
        setallpix(Colors3[4])
        print("Set color to green")
    elif command == b"blue":
        setallpix(Colors3[9])
        print("Set color to blue")
    elif command == b"random":
        setallpix(Colors3[random.randint(0,9)])
        print("Set color to random")
    elif command == b"clear":
        clear()
        print("Cleared all LEDs")
    else:
        print(f"Unknown command: {command}")

print("Starting LED control program...")
clear()  # Start with all LEDs off

print("LED control program is running. Waiting for commands...")

while True:
    if uart.any():
        try:
            command = uart.readline().strip()
            if command:
                handle_command(command)
            else:
                print("Received empty command")
        except Exception as e:
            print(f"Error processing command: {e}")
