import time, sys, os, ast, signal
import queue
import threading
#from apriltag_detector import AprilTagDetector
from phoenix6 import controls, configs, hardware, signals, unmanaged

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from web_control.tank_drive_server import run_teleop_server
from lidar.lidar import lidar_loop

lidar_enabled=False

talonfx_left = hardware.TalonFX(1)
talonfx_right = hardware.TalonFX(2)
motor_request = controls.DutyCycleOut(0.0)
LOOP_PERIOD = 0.01994  # slightly less than 20ms

# Initialize queues
lidar_queue = queue.Queue(2)
auto_queue = queue.Queue()
teleop_queue = queue.Queue(2)

# Initialize variables
last_pid_command_finished = True
current_position = [0.0, 0.0, 0.0]  # [x, y, theta]

obstacle_signal=True #default to true to be safe. 
no_lidar_count=0
# Initialize AprilTag detector
#apriltag_detector = AprilTagDetector()

def signal_handler(signal, frame):
    print('Received Ctrl+C, exiting...')
    sys.exit(0)

def periodic():
    global current_position, last_pid_command_finished, obstacle_signal, no_lidar_count

    # 0. Check the lidar queue
    if lidar_queue.empty():
        no_lidar_count+=1
        #if no_lidar_count>10: #force robot to stop if no lidar signal
        #    obstacle_signal=True
    else:
        no_lidar_count=0
        obstacle_timestamp, obstacle_signal= lidar_queue.get()
        print("got lidar signal ",obstacle_signal)

	# 1. Check the teleop queue
    if not teleop_queue.empty():
        msg_str = teleop_queue.get()
        msg_dict = ast.literal_eval(msg_str)
        left_power, right_power = msg_dict.values()
        if (left_power <= 0 and right_power <= 0) or (left_power >= 0 and right_power >= 0):
            limit_factor = 0.1
        else:
            limit_factor = 0.5
        left_power = left_power*limit_factor
        right_power = -right_power*limit_factor
        if lidar_enabled and obstacle_signal==True:
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

    # 2. Check the auto queue
    if not auto_queue.empty():
        direction, distance = auto_queue.get()
        # Process motion segment command if the last PID command is finished
        if last_pid_command_finished:
            # Start a new PID command (e.g., turning or driving straight)
            last_pid_command_finished = False

    # 3. Check if the last PID command is finished
    if not last_pid_command_finished:
        # Check if the current PID command is finished
        if is_pid_command_finished():
            last_pid_command_finished = True

    # 4. Check the NetworkTable for AprilTag information
    april_tag_data = get_april_tag_data()
    if april_tag_data:
        # Update the robot's current position based on AprilTag data
        current_position = update_position(current_position, april_tag_data)

    # 5. Process camera AprilTag detection
    camera_april_tag_data = process_camera_april_tags()
    if camera_april_tag_data:
        # Update the robot's current position based on camera AprilTag data
        current_position = update_position(current_position, camera_april_tag_data)

def is_pid_command_finished():
    # Check if the current PID command (e.g., turning or driving straight) is finished
    # Implement your logic here
    return True

def get_april_tag_data():
    # Get the latest AprilTag data from the NetworkTable
    # Implement your code to retrieve data from the NetworkTable
    return None

def process_camera_april_tags():
#    image = apriltag_detector.capture_image()
#    detections = apriltag_detector.detect_tags(image)
#    if detections:
        # For simplicity, we'll use the first detected tag
#        return detections[0]['pose']
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
    while True:
        # Call the periodic function
        periodic_start_time = time.time()
        periodic()
        periodic_end_time = time.time()

        # Calculate the time taken by the periodic function
        periodic_time = periodic_end_time - periodic_start_time

        # Calculate the remaining time in the loop
        remaining_time = LOOP_PERIOD - periodic_time

        # If there is time remaining, sleep for that duration
        if remaining_time > 0:
            time.sleep(remaining_time)

        # Calculate the loop time for the next iteration
        loop_end_time = time.time()
        loop_time = loop_end_time - start_time
        start_time = loop_end_time

        # Print the loop time for debugging purposes
        #print(f"Loop time: {loop_time * 1000:.3f}ms")

if __name__ == "__main__":
    #, args=(teleop_queue,)
    signal.signal(signal.SIGINT, signal_handler)

    main_loop_thread = threading.Thread(target=main_loop)
    main_loop_thread.start()

    if lidar_enabled:
        lidar_loop_thread = threading.Thread(target=lidar_loop,args=(lidar_queue,))
        lidar_loop_thread.start()

    try:
        run_teleop_server(teleop_queue)
    except KeyboardInterrupt:
        print('Received Ctrl+C, exiting...')
        sys.exit(0)

