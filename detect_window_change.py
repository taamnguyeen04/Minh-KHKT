import time
import pygetwindow as gw
import psutil
import pyautogui

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

    def track_activity(self):
        while True:
            current_window = self.get_active_window()
            current_process = self.get_active_process()

            if current_window != self.last_window:
                print(f"🔄 Chuyển cửa sổ: {current_window}")
                self.last_window = current_window

            if current_process != self.last_process:
                print(f"🖥️ Chuyển ứng dụng: {current_process}")
                self.last_process = current_process

            if "Chrome" in current_process or "Firefox" in current_process or "Edge" in current_process:
                pyautogui.hotkey("ctrl", "l")
                time.sleep(0.2)
                pyautogui.hotkey("ctrl", "c")
                url = pyautogui.paste()
                if url != self.last_url and url.startswith("http"):
                    print(f"🌐 Chuyển trang web: {url}")
                    self.last_url = url

            time.sleep(1)

if __name__ == "__main__":
    tracker = ActivityTracker()
    tracker.track_activity()
