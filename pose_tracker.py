import cv2
import numpy as np
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

class PoseTracker:
    def __init__(self, model_path='pose_landmarker_heavy.task', focal_length=500):
        self.focal_length = focal_length
        absolute_model_path = os.path.abspath(model_path)  # Chuyển sang đường dẫn tuyệt đối
        base_options = python.BaseOptions(model_asset_path=absolute_model_path)
        options = vision.PoseLandmarkerOptions(base_options=base_options, output_segmentation_masks=True)
        
        try:
            print("Bắt đầu khởi tạo PoseLandmarker...")
            self.detector = vision.PoseLandmarker.create_from_options(options)
            print("Khởi tạo thành công!")
        except Exception as e:
            print("Lỗi khi khởi tạo PoseLandmarker:", e)
            self.detector = None

    def is_sitting_straight(self, left_shoulder, right_shoulder):
        y_difference = abs(left_shoulder.y - right_shoulder.y)
        return y_difference < 0.1

    def estimate_eye_to_screen_distance(self, left_eye, right_eye, image_width):
        eye_to_eye_distance_cm = 6.3
        x1, x2 = left_eye.x * image_width, right_eye.x * image_width
        y1, y2 = left_eye.y * image_width, right_eye.y * image_width
        eye_distance_pixels = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return (eye_to_eye_distance_cm * self.focal_length) / eye_distance_pixels if eye_distance_pixels > 0 else None

    def process_frame(self, frame):
        if self.detector is None:
            print(0)
            return frame, "Error", None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.detector.detect(mp_image)
        
        if not detection_result.pose_landmarks:
            print(1)
            return frame, "No Pose", None

        pose_landmarks = detection_result.pose_landmarks[0]
        left_shoulder, right_shoulder = pose_landmarks[11], pose_landmarks[12]
        left_eye, right_eye = pose_landmarks[2], pose_landmarks[5]
        
        status = "Sitting straight" if self.is_sitting_straight(left_shoulder, right_shoulder) else "Not sitting straight"
        eye_distance = self.estimate_eye_to_screen_distance(left_eye, right_eye, frame.shape[1])
        
        annotated_image = frame.copy()
        cv2.putText(annotated_image, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if status == "Sitting straight" else (0, 0, 255), 2)
        if eye_distance:
            cv2.putText(annotated_image, f"Distance: {eye_distance:.2f} cm", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z) for lm in pose_landmarks])
        solutions.drawing_utils.draw_landmarks(annotated_image, pose_landmarks_proto, solutions.pose.POSE_CONNECTIONS, solutions.drawing_styles.get_default_pose_landmarks_style())
        
        return annotated_image, status, eye_distance
