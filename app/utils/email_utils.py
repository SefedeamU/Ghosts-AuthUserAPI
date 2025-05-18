import smtplib
from email.mime.text import MIMEText
import os
from string import Template

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def load_template(template_name: str, context: dict):
    template_path = os.path.join(os.path.dirname(__file__), "email_templates", template_name)
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())
    return template.safe_substitute(context)


def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, [to_email], msg.as_string())
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
        raise