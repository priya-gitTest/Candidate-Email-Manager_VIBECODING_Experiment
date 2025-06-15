import smtplib
from email.message import EmailMessage
from app.database import read_template

EMAIL_ADDRESS = "you@example.com"
EMAIL_PASSWORD = "yourpassword"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def send_email(to_address: str, subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def send_next_email(candidate_id, name, email, stage):
    if stage >= 3:
        return False
    body = read_template(stage + 1).replace("{name}", name)
    subject = f"Stage {stage + 1} - Update"
    send_email(email, subject, body)
    return True