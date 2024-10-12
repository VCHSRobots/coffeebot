import time
from phoenix6 import hardware, controls

# Constants
INCHES_PER_ROTATION = 18.85  # Assuming 6-inch wheels (pi * diameter)
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

    def get_segments(self):
        if self.is_to_ssb:
            return [
                (220, 0),   # Segment 1: Move forward 220 inches
                (1983, 90),  # Segment 2: Turn 90 degrees, move forward 1983 inches
                (620, 90)   # Segment 3: Turn 90 degrees, move forward 620 inches
            ]
        else:
            return [
                (620, 0),   # Segment 1: Move forward 620 inches
                (1983, -90),  # Segment 2: Turn -90 degrees, move forward 1983 inches
                (220, -90)   # Segment 3: Turn -90 degrees, move forward 220 inches
            ]

    def start_next_segment(self):
        if self.current_segment < len(self.segments):
            distance, turn_angle = self.segments[self.current_segment]
            self.start_position = self.talonfx_left.get_position().value
            if turn_angle != 0:
                self.is_turning = True
                self.target_position = self.start_position + (turn_angle / 360) * (ROBOT_WIDTH * 3.14159) / INCHES_PER_ROTATION
            else:
                self.is_turning = False
                self.target_position = self.start_position + distance / INCHES_PER_ROTATION
            self.current_segment += 1
            return True
        return False

    def update(self, obstacle_detected):
        if obstacle_detected:
            self.stop_motors()
            return True

        current_position = self.talonfx_left.get_position().value
        if abs(current_position - self.target_position) > 0.1:  # Allow for some tolerance
            if self.is_turning:
                self.turn()
            else:
                self.move_forward()
            return True
        else:
            self.stop_motors()
            return self.start_next_segment()

    def move_forward(self):
        self.motor_request.output = 0.3  # Adjust this value for desired speed
        self.talonfx_left.set_control(self.motor_request)
        self.talonfx_right.set_control(self.motor_request)

    def turn(self):
        turn_direction = 1 if self.is_to_ssb else -1
        self.motor_request.output = 0.2 * turn_direction
        self.talonfx_left.set_control(self.motor_request)
        self.motor_request.output = -0.2 * turn_direction
        self.talonfx_right.set_control(self.motor_request)

    def stop_motors(self):
        self.motor_request.output = 0
        self.talonfx_left.set_control(self.motor_request)
        self.talonfx_right.set_control(self.motor_request)

    def reset(self):
        self.current_segment = 0
        self.target_position = 0
        self.start_position = 0
        self.is_turning = False
