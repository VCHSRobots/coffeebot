from machine import Pin
import time
from neopixel import NeoPixel

led = Pin(25, Pin.OUT)
neopin = Pin(16, Pin.OUT)
switchpin = Pin(15, Pin.IN, Pin.PULL_UP)
n = 80
np = NeoPixel(neopin, n)
for i in range(n):
  np[i] = (255, 255, 255)
np.write()
time.sleep(2.0)

def clear():
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

def flashleds(c):
    clear()
    for i in range(n):
        np[i] = c
        np.write()
        time.sleep(0.02)
    time.sleep(0.5)
    clear()
    
clear()
time.sleep(1)
colors = ((255, 0, 0),
          (0, 255, 0),
          (0, 0, 255),
          (0, 255, 255),
          (255, 255, 0),
          (255, 255, 255))

nextcolor = 0
while True:
    if switchpin.value() == 0:
        nextcolor += 1
        if nextcolor > 5: nextcolor = 0
        flashleds(colors[nextcolor])
    

  

    


