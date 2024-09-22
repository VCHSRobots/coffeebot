from machine import Pin
import time
from neopixel import NeoPixel
import random
import math

NUM_Led = int(80)
led = Pin(25, Pin.OUT)
neopin = Pin(16, Pin.OUT)
switchpin = Pin(15, Pin.IN, Pin.PULL_UP)
np = NeoPixel(neopin, NUM_Led)

def clear():
    for i in range(NUM_Led):
        np[i] = (0, 0, 0)
    np.write()

def setallpix(color): #needs a np.write() cmd after calling
    clear()
    for i in range(NUM_Led):
            np[i] = (color)

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
        
def Snake(color_num, delay, direction, bright):
    if direction == -1:
        np[NUM_Led - 1] = adjust_brightness(Colors1[color_num],bright);
        np.write();
        time.sleep(delay);
    else:
        np[0] = adjust_brightness(Colors2[color_num], bright);
        np.write();
        time.sleep(delay);
    for i in range(1,NUM_Led/2):
        np[i * 2 * direction -1] = adjust_brightness(Colors1[color_num], bright);
        np[i * 2 * direction] = adjust_brightness(Colors2[color_num], bright);
        np.write();
        time.sleep(delay);
    if direction == 1:
        np[NUM_Led - 1] = adjust_brightness(Colors1[color_num], bright);
        np.write();
        time.sleep(delay);
    else:
        np[0] = adjust_brightness(Colors2[color_num], bright);
        np.write();
        time.sleep(delay);

Colors1 = [
    (250,21,197), #Spring Pastel Pink 0
    (7,42,218), #Summer Deep Blue 1
    (212, 12, 2), #Fall Red 2
    (255,2, 0), #Winter Red 3
];

Colors2 = [
    (176,250,135), #Spring Pastel Green 0
    (0,94,24), #Summer Cyan Blue 1
    (212, 91, 18), #Fall Orange 2
    (0,212,10), #Winter Green 3
];

while True:
#        Snake(random.randint(0,3),0.03,-1, 0.5);
#        time.sleep(0.3);
#        clear();
#        time.sleep(0.3);
#        Snake(random.randint(0,3),0.03,1, 0.5);
#        time.sleep(0.3);
#        clear();
#        time.sleep(0.3);
    if  switchpin.value() == 0:
        clear()
        time.sleep(0.1)
        setallpix(Colors1[random.randint(0,3)])
        np.write()