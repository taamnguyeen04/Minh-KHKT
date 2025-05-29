import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

def send_email_with_image(textt, image_path=None, text_path = None):
    receiver_email = "nguyentranminhtam04@gmail.com"
    sender_email = "tam.nguyentranminh04@hcmut.edu.vn"
    password = "toeu xjcj wgog lyav"

    msg = MIMEMultipart()
    msg["Subject"] = "Email có ảnh đính kèm"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    text = MIMEText(textt)
    msg.attach(text)
    # Thêm nội dung văn bản nếu có
    if text_path and os.path.exists(text_path):
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()
        msg.attach(MIMEText(text, "plain", "utf-8"))

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            image = MIMEImage(img_data, name=os.path.basename(image_path))
            msg.attach(image)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# send_email_with_image("mail có ảnh", "1.jpg")
# send_email_with_image("mail không ảnh")
