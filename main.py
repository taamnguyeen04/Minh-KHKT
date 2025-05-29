import cv2
import time
import pygetwindow as gw
import psutil
import pyautogui
import pygame
import os
from pose_tracker import PoseTracker
from eye_tracker import EyeTracker
from alo_email import send_email_with_image
from gtts import gTTS

# --- Class ActivityTracker (không dùng vòng while riêng nữa) ---
class ActivityTracker:
    def __init__(self):
        self.last_window = self.get_active_window()
        self.last_process = self.get_active_process()
        self.last_url = ""

    def get_active_window(self):
        win = gw.getActiveWindow()
        return win.title if win else "Không xác định"

    def get_active_process(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                return proc.info['name']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return "Không xác định"

    def update(self):
        current_window = self.get_active_window()
        current_process = self.get_active_process()

        if current_window != self.last_window:
            print(f"🔄 Chuyển cửa sổ: {current_window}")
            send_email_with_image(f"🔄 Chuyển cửa sổ: {current_window}")
            self.last_window = current_window

        if current_process != self.last_process:
            print(f"🖥️ Chuyển ứng dụng: {current_process}")
            send_email_with_image(f"🖥️ Chuyển ứng dụng: {current_process}")
            self.last_process = current_process

        if "Chrome" in current_process or "Firefox" in current_process or "Edge" in current_process:
            pyautogui.hotkey("ctrl", "l")
            time.sleep(0.2)
            pyautogui.hotkey("ctrl", "c")
            url = pyautogui.paste()
            if url != self.last_url and url.startswith("http"):
                print(f"🌐 Chuyển trang web: {url}")
                send_email_with_image(f"🌐 Chuyển trang web: {url}")
                self.last_url = url

# --- Text to speech ---
def text_to_speech(text, filename="temp_speech.mp3", language='vi'):
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        if os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                print("Không thể xóa file âm thanh cũ.")
                return False

        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        return True
    except Exception as e:
        print("Lỗi khi phát âm thanh:", e)
        return False
# --- Init ---
pygame.init()
pygame.mixer.init()
pose_tracker = PoseTracker()
eye_tracker = EyeTracker(sleep_threshold=5.0)
cap = cv2.VideoCapture(0)
tracker = ActivityTracker()  # khởi tạo để dùng trong while

# --- Main loop ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Cập nhật theo dõi cửa sổ mỗi vòng lặp
    tracker.update()

    # Eye tracking + pose tracking
    frame, is_sleep = eye_tracker.detect_eye_state(frame)
    annotated_frame, status, eye_distance = pose_tracker.process_frame(frame)

    print(f"Pose Status: {status}")
    print(f"eye_distance: {eye_distance:.2f} cm" if eye_distance else "Eye distance not calculated")
    print(f"Eye State: {'Asleep' if is_sleep else 'Awake'}")

    cv2.imshow('Pose Tracking', annotated_frame)

    # Phản hồi giọng nói
    # if is_sleep:
    #     text_to_speech("Bạn ơi, đừng ngủ trong lúc học, hãy ngồi thẳng lên bạn nhé", language="vi")
    # if status == "Not sitting straight":
    #     text_to_speech("Bạn đang ngồi nghiêng, hãy ngồi thẳng lưng lên bạn nhé", language="vi")
    # if eye_distance and eye_distance < 40:
    #     text_to_speech("Bạn đang ngồi gần màn hình quá, hãy ngồi xa ra bạn nhé", language="vi")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
