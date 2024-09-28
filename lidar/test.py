#!/usr/bin/python3
import itertools
from sweeppy import Sweep

with Sweep('/dev/ttyUSB0') as sweep:
    speed = sweep.get_motor_speed()
    rate = sweep.get_sample_rate()

    print('Motor Speed: {} Hz'.format(speed))
    print('Sample Rate: {} Hz'.format(rate))

    sweep.set_motor_speed(5)
    sweep.set_sample_rate(500)

    # Starts scanning as soon as the motor is ready
    sweep.start_scanning()

    # get_scans is coroutine-based generator lazily returning scans ad infinitum
    for scan in itertools.islice(sweep.get_scans(), 300):
        print(scan)
        #for s in scan.samples:
        #    if (s.distance<100 and s.signal_strength>100):
        #        print(s)


