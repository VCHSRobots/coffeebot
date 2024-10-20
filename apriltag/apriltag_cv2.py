import cv2
import numpy as np
import os
import math

# Set up the AprilTag dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
aruco_params = cv2.aruco.DetectorParameters()

# Initialize the detector
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

# Open the default camera
cap = cv2.VideoCapture(0)

# Create a directory to store the output images
output_dir = 'apriltag_output'
os.makedirs(output_dir, exist_ok=True)

# Camera calibration parameters (replace these with your actual calibrated values)
camera_matrix = np.array([
    [800, 0, 320],
    [0, 800, 240],
    [0, 0, 1]
], dtype=np.float32)
dist_coeffs = np.array([0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)

tag_size = 0.1016 # 4 inches in meters

# Define the 3D points of the AprilTag (assuming it's planar)
object_points = np.array([
    [-tag_size/2, tag_size/2, 0],
    [tag_size/2, tag_size/2, 0],
    [tag_size/2, -tag_size/2, 0],
    [-tag_size/2, -tag_size/2, 0]
], dtype=np.float32)

# Process 100 frames
for frame_count in range(100):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print(f"Failed to capture frame {frame_count}")
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect AprilTags
    corners, ids, rejected = detector.detectMarkers(gray)

    # If at least one tag is detected
    if ids is not None:
        # Draw the detected tags
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # Loop through each detected AprilTag
        for i, corner in enumerate(corners):
            # Extract the tag's ID
            tag_id = ids[i][0]

            # Calculate the center of the tag
            center = np.mean(corner[0], axis=0).astype(int)

            # Estimate pose for this marker
            success, rvec, tvec = cv2.solvePnP(object_points, corner[0], camera_matrix, dist_coeffs)

            if success:
                # Draw axis for the ArUco marker
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, 0.1)

                # Extract translation vector (position)
                x, y, z = tvec.flatten()

                # Calculate angle (assuming rotation around y-axis)
                # Extract the first elements from rvec to avoid the deprecation warning
                angle = math.atan2(rvec[2, 0], rvec[0, 0])
                angle_deg = math.degrees(angle)

                # Draw the tag ID and pose information
                cv2.putText(frame, f"ID: {tag_id}", (center[0], center[1] - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f"x: {x:.2f}, y: {y:.2f}, z: {z:.2f}", (center[0], center[1] - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f"Angle: {angle_deg:.2f} deg", (center[0], center[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                print(f"Frame {frame_count}: Detected AprilTag ID {tag_id}")
                print(f"  Position: x={x:.2f}, y={y:.2f}, z={z:.2f}")
                print(f"  Angle: {angle_deg:.2f} degrees")

    # Save the processed frame
    output_path = os.path.join(output_dir, f'frame_{frame_count:03d}.jpg')
    cv2.imwrite(output_path, frame)

    print(f"Saved frame {frame_count} to {output_path}")

# Release the capture
cap.release()

print("Processing complete. Check the 'apriltag_output' directory for the processed frames.")
