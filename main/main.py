import time, sys, os, ast, signal
import queue
import threading
import numpy as np
from phoenix6 import controls, configs, hardware, signals, unmanaged
from sys import platform
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
if platform == "linux" or platform == "linux2":
    import RPi.GPIO as GPIO
    from lidar.lidar import lidar_loop

from web_control.tank_drive_server import run_teleop_server
from auto.autonomous_path import AutonomousPath
# from apriltag_detector import AprilTagDetector
from mqtt.mqtt_handler import MQTTHandler

lidar_enabled = False

talonfx_left = hardware.TalonFX(1)
talonfx_right = hardware.TalonFX(2)
motor_request = controls.DutyCycleOut(0.0)
LOOP_PERIOD = 0.01994  # slightly less than 20ms

# Initialize queues
lidar_queue = queue.Queue(2)
auto_queue = queue.Queue()
teleop_queue = queue.Queue(2)

# Initialize variables
current_position = [0.0, 0.0, 0.0]  # [x, y, theta]
obstacle_signal = True  # default to true to be safe
no_lidar_count = 0
last_pid_command_finished = True

# Initialize autonomous paths
autonomous_path = AutonomousPath(talonfx_left, talonfx_right, motor_request)
is_autonomous = False
is_going_to_ssb = True  # True if going to SSB, False if returning to library

# Initialize AprilTag detector
# apriltag_detector = AprilTagDetector()

# Initialize MQTT handler
mqtt_handler = MQTTHandler()

# GPIO setup
BUTTON_PIN = 18  # You can change this to the actual GPIO pin you're using
ESTOP_PIN = 23  # E-Stop button pin
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(ESTOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# E-Stop variables
is_estopped = False
estop_release_time = 0

def signal_handler(signal, frame):
    print('Received Ctrl+C, exiting...')
    # GPIO.cleanup()  # Clean up GPIO on exit
    sys.exit(0)

def start_autonomous_path():
    global is_autonomous, is_going_to_ssb
    is_autonomous = True
    autonomous_path.is_to_ssb = is_going_to_ssb
    autonomous_path.reset()
    autonomous_path.start_next_segment()
    print(f"Starting path {'from Library to SSB' if is_going_to_ssb else 'from SSB to Library'}")
    mqtt_handler.report_new_run("to_ssb" if is_going_to_ssb else "to_library")
    is_going_to_ssb = not is_going_to_ssb  # Toggle the direction for next press

def button_callback(channel):
    print("Button pressed, starting autonomous path")
    start_autonomous_path()

def estop_callback(channel):
    global is_estopped, estop_release_time
    if GPIO.input(ESTOP_PIN) == GPIO.LOW:
        print("E-Stop pressed, stopping robot")
        is_estopped = True
        stop_motors()
        mqtt_handler.report_estop(True)
    else:
        print("E-Stop released, robot will resume in 1 second")
        estop_release_time = time.time() + 1  # Set release time to 1 second from now
        mqtt_handler.report_estop(False)

# GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)
# GPIO.add_event_detect(ESTOP_PIN, GPIO.BOTH, callback=estop_callback, bouncetime=300)

def stop_motors():
    motor_request.output = 0
    talonfx_left.set_control(motor_request)
    talonfx_right.set_control(motor_request)

def periodic():
    global current_position, obstacle_signal, no_lidar_count, is_autonomous, last_pid_command_finished, is_estopped, estop_release_time

    # Check E-Stop status
    if is_estopped:
        if time.time() >= estop_release_time:
            is_estopped = False
            print("E-Stop delay complete, resuming operation")
            mqtt_handler.report_estop(False)
        else:
            return  # Skip the rest of the periodic function if E-Stop is active

    # 0. Check the lidar queue
    if lidar_queue.empty():
        no_lidar_count += 1
        if no_lidar_count > 10:  # force robot to stop if no lidar signal
            obstacle_signal = False
    else:
        no_lidar_count = 0
        obstacle_timestamp, obstacle_signal = lidar_queue.get()
        print("got lidar signal ", obstacle_signal)

    # 1. Handle autonomous or teleop mode
    if is_autonomous:
        if not autonomous_path.update(obstacle_signal):
            is_autonomous = False
            print(f"{'Arrived at SSB' if autonomous_path.is_to_ssb else 'Returned to Library'}")
    elif not teleop_queue.empty():
        msg_str = teleop_queue.get()
        msg_dict = ast.literal_eval(msg_str)
        left_power, right_power = msg_dict.values()
        if (left_power <= 0 and right_power <= 0) or (left_power >= 0 and right_power >= 0):
            limit_factor = 0.1
        else:
            limit_factor = 0.5
        left_power = left_power * limit_factor
        right_power = -right_power * limit_factor
        if lidar_enabled and obstacle_signal:
            print("obstacle detected")
        else:
            unmanaged.feed_enable(0.100)
            motor_request.output = left_power
            talonfx_left.set_control(motor_request)
            motor_request.output = right_power
            talonfx_right.set_control(motor_request)
            # Get the position signal
            position_signal = talonfx_left.get_position()
            encoder_value = position_signal.value
            print(f"Current encoder value: {encoder_value}")

        # Report speed via MQTT
        average_speed = (abs(left_power) + abs(right_power)) / 2
        mqtt_handler.report_speed(average_speed)

    # 2. Check if the last PID command is finished
    if not last_pid_command_finished:
        if is_pid_command_finished():
            last_pid_command_finished = True

    # 3. Process camera AprilTag detection
    #camera_april_tag_data = process_camera_april_tags()
    #if camera_april_tag_data:
    #    current_position = update_position(current_position, camera_april_tag_data)

    # Report position via MQTT
    mqtt_handler.report_position(current_position[0], current_position[1], current_position[2])

    # TODO: Add battery level reporting when available
    # battery_level = get_battery_level()
    # mqtt_handler.report_battery(battery_level)

def is_pid_command_finished():
    # Check if the current PID command (e.g., turning or driving straight) is finished
    # Implement your logic here
    return True

def get_april_tag_data():
    # Get the latest AprilTag data from the NetworkTable
    # Implement your code to retrieve data from the NetworkTable
    return None

def process_camera_april_tags():
    image = apriltag_detector.capture_image()
    detections = apriltag_detector.detect_tags(image)
    if detections:
        # For simplicity, we'll use the first detected tag
        return detections[0]['pose']
    return None

def update_position(current_position, new_pose):
    # Implement your logic to update the current position based on the new pose
    # This is a simplified example and may need to be adjusted based on your coordinate system
    x = new_pose[0, 3]
    y = new_pose[1, 3]
    theta = np.arctan2(new_pose[1, 0], new_pose[0, 0])
    return [x, y, theta]

def main_loop():
    print("Starting main control loop...")
    start_time = time.time()
    start_autonomous_path()
    while True:
        periodic_start_time = time.time()
        periodic()
        periodic_end_time = time.time()

        periodic_time = periodic_end_time - periodic_start_time
        remaining_time = LOOP_PERIOD - periodic_time

        if remaining_time > 0:
            time.sleep(remaining_time)

        loop_end_time = time.time()
        loop_time = loop_end_time - start_time
        start_time = loop_end_time

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    main_loop_thread = threading.Thread(target=main_loop)
    main_loop_thread.start()

    if lidar_enabled:
        lidar_loop_thread = threading.Thread(target=lidar_loop, args=(lidar_queue,))
        lidar_loop_thread.start()

    try:
        run_teleop_server(teleop_queue)
    except KeyboardInterrupt:
        print('Received Ctrl+C, exiting...')
        # GPIO.cleanup()  # Clean up GPIO on exit
        sys.exit(0)
