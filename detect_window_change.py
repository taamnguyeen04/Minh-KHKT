import time
import pygetwindow as gw
import psutil
import pyautogui

def get_active_window():
    win = gw.getActiveWindow()
    return win.title if win else "Không xác định"

def get_active_process():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            return proc.info['name']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return "Không xác định"

last_window = get_active_window()
last_process = get_active_process()
last_url = ""

while True:
    current_window = get_active_window()
    current_process = get_active_process()

    if current_window != last_window:
        print(f"🔄 Chuyển cửa sổ: {current_window}")
        last_window = current_window

    if current_process != last_process:
        print(f"🖥️ Chuyển ứng dụng: {current_process}")
        last_process = current_process

    if "Chrome" in current_process or "Firefox" in current_process or "Edge" in current_process:
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "c")
        url = pyautogui.paste()
        if url != last_url and url.startswith("http"):
            print(f"🌐 Chuyển trang web: {url}")
            last_url = url

    time.sleep(1)
