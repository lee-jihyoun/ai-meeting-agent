# 요약된 내용을 이메일 발송
import smtplib
from email.mime.text import MIMEText

# TODO : your@email.com 직접 입력 대신에 -> .env 에서 받아오도록 처리 필요
def send_summary_email(summary, to_emails):
    msg = MIMEText(summary)
    msg["Subject"] = "회의 요약 내용"
    msg["From"] = "your@email.com"
    msg["To"] = ", ".join(to_emails)

# TODO : 이메일서버("smtp.yourmailserver.com"), 
# 로그인정보("your@email.com", "yourpassword") 
# 전부 다 .env 에서 받아오도록 처리 필요
    with smtplib.SMTP("smtp.yourmailserver.com", 587) as server:
        server.starttls()
        server.login("your@email.com", "yourpassword")
        server.sendmail(msg["From"], to_emails, msg.as_string())
