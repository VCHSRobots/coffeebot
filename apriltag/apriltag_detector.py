import cv2
from pupil_apriltags import Detector
import numpy as np

class AprilTagDetector:
    def __init__(self):
        self.detector = Detector(families='tag36h11',
                                 nthreads=1,
                                 quad_decimate=1.0,
                                 quad_sigma=0.0,
                                 refine_edges=1,
                                 decode_sharpening=0.25,
                                 debug=0)
        
        # Camera parameters (adjust these based on your camera)
        self.camera_matrix = np.array([[1000, 0, 320],
                                       [0, 1000, 240],
                                       [0, 0, 1]], dtype=np.float32)
        self.dist_coeffs = np.zeros((4, 1))

    def detect_tags(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        tags = self.detector.detect(gray, estimate_tag_pose=True, camera_params=self.camera_matrix, tag_size=0.15)
        
        detections = []
        for tag in tags:
            pose = self.get_pose_from_tag(tag)
            detections.append({
                'id': tag.tag_id,
                'pose': pose
            })
        
        return detections

    def get_pose_from_tag(self, tag):
        rotation_matrix, _ = cv2.Rodrigues(tag.pose_R)
        translation_vector = tag.pose_t
        
        # Combine rotation and translation into a 4x4 transformation matrix
        transform = np.eye(4)
        transform[:3, :3] = rotation_matrix
        transform[:3, 3] = translation_vector.flatten()
        
        return transform

    def capture_image(self):
        # Implement camera capture logic here
        # For now, we'll return a dummy image
        return np.zeros((480, 640, 3), dtype=np.uint8)
