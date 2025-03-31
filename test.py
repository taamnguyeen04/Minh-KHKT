import os
print("Current working directory:", os.getcwd())
try:
    with open("pose_landmarker_heavy.task", "rb") as f:
        print("File mở thành công!")
except FileNotFoundError:
    print("Không tìm thấy tệp!")
except Exception as e:
    print("Lỗi khác:", e)
