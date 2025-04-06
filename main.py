import cv2
from pose_tracker import PoseTracker
from eye_tracker import EyeTracker
from alo_email import send_email_with_image
from detect_window_change import ActivityTracker
from gtts import gTTS
import pygame
import os

# Khởi tạo pygame mixer
pygame.init()
pygame.mixer.init()

# Khởi tạo các tracker
pose_tracker = PoseTracker()
eye_tracker = EyeTracker(sleep_threshold=5.0)
cap = cv2.VideoCapture(0)

def text_to_speech(text, filename="temp_speech.mp3", language='vi'):
    """Chuyển văn bản thành giọng nói và phát"""
    try:
        # Nếu đang phát thì dừng và unload
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # Giải phóng file đang mở

        # Xóa file cũ nếu tồn tại
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                print("Không thể xóa file âm thanh cũ.")
                return False

        # Tạo file âm thanh mới
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(filename)

        # Phát âm thanh
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Chờ phát xong
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        return True
    except Exception as e:
        print("Lỗi khi phát âm thanh:", e)
        return False


# Vòng lặp xử lý video
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Theo dõi trạng thái mắt
    frame, is_sleep = eye_tracker.detect_eye_state(frame)

    # Theo dõi tư thế và khoảng cách mắt
    annotated_frame, status, eye_distance = pose_tracker.process_frame(frame)

    print(f"Pose Status: {status}")
    print(f"eye_distance: {eye_distance:.2f} cm" if eye_distance else "Eye distance not calculated")
    print(f"Eye State: {'Asleep' if is_sleep else 'Awake'}")

    # Hiển thị khung hình
    cv2.imshow('Pose Tracking', annotated_frame)

    # Cảnh báo bằng giọng nói
    if is_sleep:
        text_to_speech("dậy đi bạn", language="vi")
    if status == "Not sitting straight":
        text_to_speech("ngồi thẳng lên bạn", language="vi")
    if eye_distance and eye_distance < 25:
        text_to_speech("ngồi xa màn hình máy tính xíu đi bạn", language="vi")

    # Thoát bằng phím 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
