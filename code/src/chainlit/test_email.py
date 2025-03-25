from tools.email_handler import EmailHandler

email_handler = EmailHandler(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="tejaswiavvaru@gmail.com",
    password="rynb deqb luam wioq"
)

email_handler.send_email(
    to_email="tejaswiavvaru@gmail.com",
    subject="Test Email",
    body="This is a test email sent via the Outlook SMTP server."
)

print("Email sent successfully!")