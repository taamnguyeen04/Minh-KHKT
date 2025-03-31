# import cv2
# from pose_tracker import PoseTracker
# from eye_tracker import EyeTracker

# pose_tracker = PoseTracker()
# tracker = EyeTracker(sleep_threshold=5.0)
# cap = cv2.VideoCapture(0)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#     frame, is_sleep = tracker.detect_eye_state(frame)
#     annotated_frame, status = pose_tracker.process_frame(frame)
#     print(f"Eye State: {state}")
#     cv2.imshow('Pose Tracking', annotated_frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

import cv2
from pose_tracker import PoseTracker
from eye_tracker import EyeTracker

pose_tracker = PoseTracker()
tracker = EyeTracker(sleep_threshold=5.0)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame, is_sleep = tracker.detect_eye_state(frame)
    annotated_frame, status, eye_distance = pose_tracker.process_frame(frame)
    print(f"Pose Status: {status}")
    print(f"eye_distance: {eye_distance:.2f} cm" if eye_distance else "Eye distance not calculated")
    print(f"Eye State: {'Asleep' if is_sleep else 'Awake'}")
    cv2.imshow('Pose Tracking', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()