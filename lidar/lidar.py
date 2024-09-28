from collections import deque
import queue
import time, itertools
from math import atan, sin, cos
from sweeppy import Sweep

# unit is feet
robot_width=2.0  # a in diagram
obstacle_range=2.0  # l in diagram
lidar_setback=1.5 # c in diagram
dejitter_time=500 # in millisecond

# Global variable to store LiDAR data
lidar_data = deque()

def convert_angle(angle):
    """
    Convert an angle from the range (0, 360*1000) to the range (-180, 180).
    Args:
        angle (int): The input angle in the range (0, 360*1000).
    Returns:
        float: The converted angle in the range (-180, 180).
    """
    # Convert the angle from the range (0, 360*1000) to (0, 360)
    angle_degrees = angle / 1000.0

    # Convert the angle from (0, 360) to (-180, 180)
    if angle_degrees > 180:
        angle_degrees -= 360

    return angle_degrees

def process_lidar_data(scan):
    global lidar_data, robot_width, obstacle_range, lidar_setback

    # Add current timestamp to each sample in the scan
    current_time = time.time() * 1000  # Timestamp in milliseconds
    count=0;
    # sample unit returned from the library, for distance is centimeter, and angle is millidesgree.
    # signal_strength is range from 0 to 256.
    for sample in scan.samples:
        #print(sample.angle, sample.distance, sample.signal_strength, len(lidar_data))
        count+=1
        if sample.signal_strength>100:
            lidar_data.append((sample, current_time))

    # Filter out data older than 200ms
    while lidar_data and lidar_data[0][1] < (current_time - dejitter_time):
        lidar_data.popleft()

    # Calculate theta
    if lidar_setback==0:
        theta=90
    else:
        theta = atan((robot_width / 2) / lidar_setback) * (180 / 3.14159265359)
    #print("theta",theta, "queue length", len(lidar_data))

    # Check for obstacles in the shaded area
    obstacle_detected = False
    for sample, _ in lidar_data:
        # Filter out samples outside the angle range
        angle = convert_angle(sample.angle)
        if angle < -theta or angle > theta:
            continue

        # Calculate x and y coordinates
        #print("sample ",sample.angle, sample.distance, sample.signal_strength)
        d = sample.distance * 0.01 * 3.28084 # turn meter to feet
        alpha = angle * (3.14159265359 / 180)  # Convert angle to radians
        x = d * sin(alpha)
        y = d * cos(alpha) - lidar_setback

        # Check if the obstacle is within the shaded region
        if abs(x) < (robot_width / 2) and abs(y) < obstacle_range:
            print("d in feet ",d,"alpha",alpha,"x/y",x,y)
            obstacle_detected = True
            break

    # Send yes/no signal to the main control loop every 20ms
    return obstacle_detected

def lidar_loop(lidar_queue):
    with Sweep('/dev/ttyUSB0') as sweep:
        speed = sweep.get_motor_speed()
        rate = sweep.get_sample_rate()

        print('Motor Speed: {} Hz'.format(speed))
        print('Sample Rate: {} Hz'.format(rate))

        sweep.set_motor_speed(5)
        sweep.set_sample_rate(500)

        # Starts scanning as soon as the motor is ready
        sweep.start_scanning()

        # Get scans and process LiDAR data
        #for scan in itertools.islice(sweep.get_scans(), 300):
        for scan in sweep.get_scans():
            signal = process_lidar_data(scan)
            timestamp=time.time() * 1000
            print(f"Time: {timestamp}, Obstacle: {signal}")
            try:
                lidar_queue.put((timestamp,signal), block=False)
            except queue.Full:
                print("lidar queue is full, cannot add message")


if __name__ == "__main__":
    lidar_queue = queue.Queue(2)
    lidar_loop(lidar_queue)
