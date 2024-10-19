import time
from phoenix6 import hardware, controls

# Constants
INCHES_PER_TICK = 2.4 # Assuming 20ms tick time
ROBOT_WIDTH = 24  # Assuming the robot is 24 inches wide

class AutonomousPath:
    def __init__(self, talonfx_left, talonfx_right, motor_request, is_to_ssb=True):
        self.talonfx_left = talonfx_left
        self.talonfx_right = talonfx_right
        self.motor_request = motor_request
        self.current_segment = 0
        self.is_to_ssb = is_to_ssb
        self.segments = self.get_segments()
        self.target_position = 0
        self.start_position = 0
        self.is_turning = False
        self.forward_counter = 0
        self.segment_completed = False
        self.turn_completed = False
        print(f"[DEBUG] AutonomousPath initialized. Is to SSB: {self.is_to_ssb}")

    def get_segments(self):
        if self.is_to_ssb:
            segments = [
                (220, 0),   # Segment 1: Move forward 220 inches
                (1983, -90),  # Segment 2: Turn 90 degrees, move forward 1983 inches
                (620, 90)   # Segment 3: Turn 90 degrees, move forward 620 inches
            ]
        else:
            segments = [
                (620, 0),   # Segment 1: Move forward 620 inches
                (1983, -90),  # Segment 2: Turn -90 degrees, move forward 1983 inches
                (220, 90)   # Segment 3: Turn -90 degrees, move forward 220 inches
            ]
        print(f"[DEBUG] Segments: {segments}")
        return segments

    def start_next_segment(self):
        if self.current_segment < len(self.segments):
            distance, turn_angle = self.segments[self.current_segment]
            self.forward_counter = 0  # Reset counter for new segment
            self.start_position = self.forward_counter
            self.is_turning = turn_angle != 0
            self.turn_completed = False
            
            if self.is_turning:
                # Set up turning phase
                self.target_position = abs(turn_angle)
            else:
                # Set up forward movement phase
                self.target_position = distance / INCHES_PER_TICK
            
            self.current_segment += 1
            self.segment_completed = False
            print(f"[DEBUG] Starting segment {self.current_segment}. Is turning: {self.is_turning}, Start position: {self.start_position}, Target position: {self.target_position}")
            return True
        print("[DEBUG] No more segments to process")
        return False

    def update(self, obstacle_detected):
        if obstacle_detected:
            print("[DEBUG] Obstacle detected, stopping motors")
            self.stop_motors()
            return True

        current_position = self.forward_counter
        print(f"[DEBUG] Current position: {current_position}, Target position: {self.target_position}")
        
        if not self.segment_completed:
            if current_position < self.target_position:
                if self.is_turning:
                    self.turn()
                else:
                    self.move_forward()
                return True
            else:
                if self.is_turning and not self.turn_completed:
                    # Transition from turning to forward movement
                    self.turn_completed = True
                    distance, _ = self.segments[self.current_segment - 1]
                    self.target_position = distance / INCHES_PER_TICK
                    self.forward_counter = 0
                    print(f"[DEBUG] Turning completed. Starting forward movement. Target position: {self.target_position}")
                    return True
                else:
                    print("[DEBUG] Reached or passed target position, stopping motors")
                    self.stop_motors()
                    self.segment_completed = True
        
        if self.segment_completed:
            return self.start_next_segment()
        
        return True

    def move_forward(self):
        self.motor_request.output = 0.3  # Adjust this value for desired speed
        self.talonfx_left.set_control(self.motor_request)
        self.talonfx_right.set_control(self.motor_request)
        self.forward_counter += 1
        print(f"[DEBUG] Moving forward. Motor output: {self.motor_request.output}")

    def turn(self):
        if not self.turn_completed:
            turn_direction = 1 if self.is_to_ssb else -1
            left_output = 0.2 * turn_direction
            right_output = -0.2 * turn_direction
            self.motor_request.output = left_output
            self.talonfx_left.set_control(self.motor_request)
            self.motor_request.output = right_output
            self.talonfx_right.set_control(self.motor_request)
            self.forward_counter += 1
            print(f"[DEBUG] Turning. Left motor output: {left_output}, Right motor output: {right_output}")
        else:
            self.move_forward()

    def stop_motors(self):
        self.motor_request.output = 0
        self.talonfx_left.set_control(self.motor_request)
        self.talonfx_right.set_control(self.motor_request)
        print("[DEBUG] Motors stopped")

    def reset(self):
        self.current_segment = 0
        self.target_position = 0
        self.start_position = 0
        self.forward_counter = 0
        self.is_turning = False
        self.segment_completed = False
        self.turn_completed = False
        print("[DEBUG] AutonomousPath reset")
