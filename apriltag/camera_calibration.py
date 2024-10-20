import numpy as np
import cv2
import glob
import os
import time
import keyboard
import threading

# Global flags for key presses
space_pressed = False
q_pressed = False

def key_capture_thread():
    global space_pressed, q_pressed
    print("Key capture thread started")  # Debug print
    while True:
        if keyboard.is_pressed('space'):
            print("Spacebar pressed (in thread)")  # Debug print
            space_pressed = True
            time.sleep(0.1)  # Debounce
        if keyboard.is_pressed('q'):
            print("Q key pressed (in thread)")  # Debug print
            q_pressed = True
            break

def capture_calibration_images():
    global space_pressed, q_pressed
    cap = cv2.VideoCapture(0)  # Open the default camera (change if necessary)
    
    # Create directory for calibration images if it doesn't exist
    if not os.path.exists('calibration_images'):
        os.makedirs('calibration_images')

    img_counter = 0
    last_capture_time = 0
    capture_delay = 0.5  # Delay between captures in seconds

    print("Press SPACEBAR to capture an image of the chessboard.")
    print("Press 'q' to finish capturing and start calibration.")

    # Start the key capture thread
    key_thread = threading.Thread(target=key_capture_thread)
    key_thread.daemon = True
    key_thread.start()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Capture Calibration Images", frame)
        cv2.waitKey(1)  # This is just to update the display

        if q_pressed:
            print("Q key pressed, exiting capture loop")  # Debug print
            break
        
        if space_pressed:
            print("Spacebar pressed, attempting to capture image")  # Debug print
            current_time = time.time()
            if current_time - last_capture_time > capture_delay:
                img_name = f"calibration_images/chessboard_{img_counter}.jpg"
                cv2.imwrite(img_name, frame)
                print(f"{img_name} written!")
                img_counter += 1
                last_capture_time = current_time
            space_pressed = False  # Reset the flag

    cap.release()
    cv2.destroyAllWindows()
    return img_counter

def calibrate_camera():
    # Chessboard dimensions
    CHESSBOARD_SIZE = (9, 6)
    SQUARE_SIZE = 0.0295 

    # Prepare object points
    objp = np.zeros((CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE

    # Arrays to store object points and image points from all images
    objpoints = []  # 3d points in real world space
    imgpoints = []  # 2d points in image plane

    # Get list of calibration images
    images = glob.glob('calibration_images/*.jpg')
    print(images)

    for fname in images:
        img = cv2.imread(fname)
        
        # Color-segmentation to get binary mask
        lwr = np.array([0, 0, 143])
        upr = np.array([179, 61, 252])
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        msk = cv2.inRange(hsv, lwr, upr)

        # Extract chess-board
        krn = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 30))
        dlt = cv2.dilate(msk, krn, iterations=5)
        res = 255 - cv2.bitwise_and(dlt, msk)

        # Convert result to uint8
        res = np.uint8(res)

        # Find the chessboard corners
        ret, corners = cv2.findChessboardCornersSB(res, CHESSBOARD_SIZE, flags=cv2.CALIB_CB_EXHAUSTIVE)
        print(ret)
        print(corners)

        if ret:
            objpoints.append(objp)
            imgpoints.append(corners)

            # Draw and display the corners
            cv2.drawChessboardCorners(img, CHESSBOARD_SIZE, corners, ret)
            cv2.imshow('img', img)
            cv2.waitKey(500)

    cv2.destroyAllWindows()

    if len(objpoints) == 0:
        print("No valid calibration images found. Calibration failed.")
        return None, None

    # Calibrate the camera
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img.shape[:2], None, None)

    # Save the camera calibration results
    np.savez('camera_calibration.npz', mtx=mtx, dist=dist)

    print("Camera matrix:")
    print(mtx)
    print("\nDistortion coefficients:")
    print(dist)

    return mtx, dist

if __name__ == "__main__":
    print("Starting calibration image capture...")  # Debug print
    num_images = capture_calibration_images()
    print(f"Captured {num_images} images.")
    
    if num_images >= 0:
        print("Starting camera calibration...")
        calibrate_camera()
    else:
        print("No images captured. Calibration cannot proceed.")
