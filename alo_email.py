import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

def send_email_with_image(text, image_path=None):
    sender_email = "tam.nguyentranminh04@hcmut.edu.vn"
    receiver_email = "nguyentranminhtam04@gmail.com"
    password = "toeu xjcj wgog lyav"

    msg = MIMEMultipart()
    msg["Subject"] = "Email có ảnh đính kèm"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    text = MIMEText("Đây là nội dung email có ảnh đính kèm.")
    msg.attach(text)

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            image = MIMEImage(img_data, name=os.path.basename(image_path))
            msg.attach(image)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

send_email_with_image("mail có ảnh", "1.jpg")
send_email_with_image("mail không ảnh")
