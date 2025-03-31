from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2


# Hàm kiểm tra tư thế ngồi thẳng
def is_sitting_straight(left_shoulder, right_shoulder):
    y_difference = abs(left_shoulder.y - right_shoulder.y)
    threshold = 0.05
    return y_difference < threshold


# Hàm tính khoảng cách từ mắt đến màn hình (chuyển đổi tọa độ về pixel trước)
def estimate_eye_to_screen_distance(left_eye, right_eye, focal_length, image_width):
    eye_to_eye_distance_cm = 6.3  # Khoảng cách thực tế giữa hai mắt

    # Chuyển đổi tọa độ từ chuẩn hóa về pixel
    x1, x2 = left_eye.x * image_width, right_eye.x * image_width
    y1, y2 = left_eye.y * image_width, right_eye.y * image_width

    # Tính khoảng cách giữa hai mắt theo pixel
    eye_distance_pixels = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # Nếu khoảng cách mắt không hợp lệ, trả về None
    if eye_distance_pixels <= 0:
        return None

    # Tính khoảng cách từ mắt đến màn hình
    estimated_distance_cm = (eye_to_eye_distance_cm * focal_length) / eye_distance_pixels

    return estimated_distance_cm


# Hàm vẽ landmarks lên ảnh và in tọa độ vai, mắt cùng thông báo
def draw_landmarks_on_image_and_print_coordinates(rgb_image, detection_result, focal_length):
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(rgb_image)
    image_height, image_width, _ = rgb_image.shape  # Lấy kích thước ảnh

    # Kiểm tra nếu không có landmarks được phát hiện
    if not pose_landmarks_list:
        return annotated_image

    # Lấy danh sách landmarks từ kết quả phát hiện
    pose_landmarks = pose_landmarks_list[0]

    # Lấy tọa độ của vai và mắt theo chỉ số chính xác
    left_shoulder = pose_landmarks[11]  # Vai trái
    right_shoulder = pose_landmarks[12]  # Vai phải
    left_eye = pose_landmarks[2]  # Mắt trái
    right_eye = pose_landmarks[5]  # Mắt phải

    # Kiểm tra tư thế ngồi
    if is_sitting_straight(left_shoulder, right_shoulder):
        cv2.putText(annotated_image, "Sitting straight", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(annotated_image, "Warning: Not sitting straight!", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Tính khoảng cách từ mắt đến màn hình
    eye_to_screen_distance = estimate_eye_to_screen_distance(left_eye, right_eye, focal_length, image_width)

    if eye_to_screen_distance:
        cv2.putText(annotated_image, f"Distance: {eye_to_screen_distance:.2f} cm", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

    # Vẽ các landmarks
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
        annotated_image,
        pose_landmarks_proto,
        solutions.pose.POSE_CONNECTIONS,
        solutions.drawing_styles.get_default_pose_landmarks_style())

    return annotated_image


if __name__ == '__main__':
    # Khởi tạo mô hình PoseLandmarker
    base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True)
    try:
        print("Bắt đầu khởi tạo PoseLandmarker...")
        detector = vision.PoseLandmarker.create_from_options(options)
        print("Khởi tạo thành công!")
    except Exception as e:
        print("Lỗi khi khởi tạo PoseLandmarker:", e)

    print("alo")

    focal_length = 500  # Giả định tiêu cự camera
    # Mở webcam
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Không thể lấy khung hình từ camera. Thoát...")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Phát hiện pose landmarks
        detection_result = detector.detect(mp_image)

        # Vẽ lên hình
        annotated_frame = draw_landmarks_on_image_and_print_coordinates(frame, detection_result, focal_length)

        cv2.imshow('Pose Detection', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()