import smtplib
from email.mime.text import MIMEText

def send_email():
    sender_email = "tam.nguyentranminh04@hcmut.edu.vn"
    receiver_email = "nguyentranminhtam04@gmail.com"
    password = "toeu xjcj wgog lyav"

    msg = MIMEText("Đây là nội dung email.")
    msg["Subject"] = "Đây là tiêu đề Email"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

send_email()
