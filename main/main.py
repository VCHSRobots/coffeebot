import time
import queue
from apriltag_detector import AprilTagDetector

LOOP_PERIOD = 0.01994  # slightly less than 20ms

# Initialize queues
lidar_queue = queue.Queue()
teleop_queue = queue.Queue()
auto_queue = queue.Queue()

# Initialize variables
last_pid_command_finished = True
current_position = [0.0, 0.0, 0.0]  # [x, y, theta]

# Initialize AprilTag detector
apriltag_detector = AprilTagDetector()

def periodic():
    global current_position, last_pid_command_finished

    # 0. Check the lidar queue
    if not lidar_queue.empty():
        obstacle_distance, obstacle_direction = lidar_queue.get()
        # Process lidar data (e.g., avoid obstacles)

    # 1. Check the teleop queue
    if not teleop_queue.empty():
        left_power, right_power = teleop_queue.get()
        # Send drive commands to motors

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

if __name__ == "__main__":
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
        print(f"Loop time: {loop_time * 1000:.3f}ms")
