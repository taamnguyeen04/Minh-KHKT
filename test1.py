import face_recognition
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from deepface import DeepFace


def calculate_psnr(img1, img2):
    """Tính PSNR giữa hai ảnh"""
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    return 10 * np.log10((max_pixel ** 2) / mse)


def calculate_ssim(img1, img2):
    """Tính SSIM giữa hai ảnh"""
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    return ssim(gray1, gray2)


def analyze_emotion(image_path):
    """Phân tích cảm xúc từ ảnh, trả về True nếu là 'happy'"""
    try:
        result = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
        dominant_emotion = result[0]['dominant_emotion']
        return dominant_emotion == 'happy'
    except:
        return False


def process_images(input_dir, cycleGan_dir, starGan_dir, starGan1_dir, validation_csv, output_csv):
    """Xử lý ảnh và tính toán các chỉ số đánh giá"""
    # Đọc danh sách ảnh trung tính từ file CSV
    df = pd.read_csv(validation_csv)
    neutral_images = df[df["expression"] == 0]["subDirectory_filePath"].tolist()

    results = []

    for img_path in neutral_images:
        img_info = img_path.split("/")
        filename = img_info[1]

        input_path = os.path.join(input_dir, filename)
        cycleGan_path = os.path.join(cycleGan_dir, filename)
        starGan_path = os.path.join(starGan_dir, filename)
        starGan1_path = os.path.join(starGan1_dir, filename)

        if not (os.path.exists(cycleGan_path) and os.path.exists(starGan_path) and os.path.exists(starGan1_path)):
            print(f"Warning: Missing generated images for {filename}")
            continue

        try:
            # Đọc ảnh bằng OpenCV để tính PSNR và SSIM
            img_input_cv = cv2.imread(input_path)

            # Đọc và resize ảnh từ các mô hình
            img_cycleGan_cv = cv2.resize(cv2.imread(cycleGan_path), (img_input_cv.shape[1], img_input_cv.shape[0]))
            img_starGan_cv = cv2.resize(cv2.imread(starGan_path), (img_input_cv.shape[1], img_input_cv.shape[0]))
            img_starGan1_cv = cv2.resize(cv2.imread(starGan1_path), (img_input_cv.shape[1], img_input_cv.shape[0]))

            # Tính PSNR và SSIM
            psnr_cycleGan = calculate_psnr(img_input_cv, img_cycleGan_cv)
            ssim_cycleGan = calculate_ssim(img_input_cv, img_cycleGan_cv)

            psnr_starGan = calculate_psnr(img_input_cv, img_starGan_cv)
            ssim_starGan = calculate_ssim(img_input_cv, img_starGan_cv)

            psnr_starGan1 = calculate_psnr(img_input_cv, img_starGan1_cv)
            ssim_starGan1 = calculate_ssim(img_input_cv, img_starGan1_cv)

            # Đọc ảnh bằng face_recognition để tính độ tương đồng khuôn mặt
            img_input_fr = face_recognition.load_image_file(input_path)
            img_cycleGan_fr = face_recognition.load_image_file(cycleGan_path)
            img_starGan_fr = face_recognition.load_image_file(starGan_path)
            img_starGan1_fr = face_recognition.load_image_file(starGan1_path)

            # Mã hóa khuôn mặt
            input_encoding = face_recognition.face_encodings(img_input_fr)
            cycleGan_encoding = face_recognition.face_encodings(img_cycleGan_fr)
            starGan_encoding = face_recognition.face_encodings(img_starGan_fr)
            starGan1_encoding = face_recognition.face_encodings(img_starGan1_fr)

            if len(input_encoding) == 0 or len(cycleGan_encoding) == 0 or len(starGan_encoding) == 0 or len(
                    starGan1_encoding) == 0:
                print(f"Warning: Không tìm thấy khuôn mặt trong ảnh {filename}")
                continue

            # Tính độ tương đồng cosine
            input_encoding = input_encoding[0].reshape(1, -1)
            cycleGan_encoding = cycleGan_encoding[0].reshape(1, -1)
            starGan_encoding = starGan_encoding[0].reshape(1, -1)
            starGan1_encoding = starGan1_encoding[0].reshape(1, -1)

            cycleGan_similarity = cosine_similarity(input_encoding, cycleGan_encoding)[0][0]
            starGan_similarity = cosine_similarity(input_encoding, starGan_encoding)[0][0]
            starGan1_similarity = cosine_similarity(input_encoding, starGan1_encoding)[0][0]

            # Phân tích cảm xúc
            input_happy = analyze_emotion(input_path)
            cycleGan_happy = analyze_emotion(cycleGan_path)
            starGan_happy = analyze_emotion(starGan_path)
            starGan1_happy = analyze_emotion(starGan1_path)

            # Lưu kết quả
            results.append([
                filename,
                psnr_cycleGan, ssim_cycleGan, cycleGan_similarity, int(cycleGan_happy),
                psnr_starGan, ssim_starGan, starGan_similarity, int(starGan_happy),
                psnr_starGan1, ssim_starGan1, starGan1_similarity, int(starGan1_happy),
                int(input_happy)
            ])

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

    # Tạo DataFrame và lưu kết quả
    results_df = pd.DataFrame(results, columns=[
        "Filename",
        "PSNR_CycleGAN", "SSIM_CycleGAN", "CycleGAN_Similarity", "CycleGAN_Happy",
        "PSNR_StarGAN", "SSIM_StarGAN", "StarGAN_Similarity", "StarGAN_Happy",
        "PSNR_StarGAN1", "SSIM_StarGAN1", "StarGAN1_Similarity", "StarGAN1_Happy",
        "Original_Happy"
    ])

    results_df.to_csv(output_csv, index=False)
    print(f"Kết quả đã được lưu vào {output_csv}")
    return results_df


# Các tham số đường dẫn
input_dir = r"C:\Users\tam\Desktop\pythonProject\input"
cycleGan_dir = r"C:\Users\tam\Desktop\pythonProject\cycleGan"
starGan_dir = r"C:\Users\tam\Desktop\pythonProject\starGan"  # Thư mục StarGAN gốc
starGan1_dir = r"C:\Users\tam\Desktop\pythonProject\starGan1"  # Thư mục StarGAN1
validation_csv = r"C:\Users\tam\Desktop\pythonProject\validation.csv"
output_csv = "final_results_with_emotion.csv"

# Chạy chương trình
results = process_images(input_dir, cycleGan_dir, starGan_dir, starGan1_dir, validation_csv, output_csv)