import cv2
import mediapipe as mp
import numpy as np
import time

class EyeTracker:
    def __init__(self, sleep_threshold=5.0):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.sleep_threshold = sleep_threshold  # Ngưỡng thời gian để xác định ngủ
        self.closed_eye_start = None  # Thời điểm bắt đầu nhắm mắt

    def eye_aspect_ratio(self, landmarks, eye_points):
        p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye_points]
        d1 = np.linalg.norm(np.array(p2) - np.array(p6))
        d2 = np.linalg.norm(np.array(p3) - np.array(p5))
        d3 = np.linalg.norm(np.array(p1) - np.array(p4))
        return (d1 + d2) / (2.0 * d3)

    def detect_eye_state(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)
        state = False # "Awake"

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = [(lm.x * frame.shape[1], lm.y * frame.shape[0]) for lm in face_landmarks.landmark]
                left_ear = self.eye_aspect_ratio(landmarks, self.LEFT_EYE)
                right_ear = self.eye_aspect_ratio(landmarks, self.RIGHT_EYE)
                avg_ear = (left_ear + right_ear) / 2.0

                for i in self.LEFT_EYE + self.RIGHT_EYE:
                    x, y = int(landmarks[i][0]), int(landmarks[i][1])
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                if avg_ear < 0.2:
                    if self.closed_eye_start is None:
                        self.closed_eye_start = time.time()
                    elapsed_time = time.time() - self.closed_eye_start
                    if elapsed_time >= self.sleep_threshold:
                        state = True #"Asleep"
                        cv2.putText(frame, "Sleep", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    else:
                        cv2.putText(frame, "Eyes Closed", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    self.closed_eye_start = None  # Reset nếu mắt mở
                    cv2.putText(frame, "Eyes Open", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame, state