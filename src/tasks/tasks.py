import smtplib
from email.message import EmailMessage

from celery import Celery

from src.core.config import setting

celery = Celery("tasks", broker=f"redis://{setting.REDIS_HOST}:{setting.REDIS_PORT}")


def get_email_for_send(username: str, friend_name: str, receiver: str):
    email = EmailMessage()
    email["Subject"] = "Ваше сообщение было лайкнуто"
    email["From"] = setting.SMTP_USER
    email["To"] = receiver

    email.set_content(
        "<div>"
        f'<h1 style="color: red;">Здравствуйте, {username}, ваш пост был лайкнут пользователем {friend_name} 😊</h1>'
        '<img src="https://static.vecteezy.com/system/resources/previews/008/295/031/original/custom-relationship'
        "-management-dashboard-ui-design-template-suitable-designing-application-for-android-and-ios-clean-style-app"
        '-mobile-free-vector.jpg" width="600">'
        "</div>",
        subtype="html",
    )
    return email


@celery.task
def send_email_report_dashboard(username: str, friend_name: str, receiver: str):
    email = get_email_for_send(username, friend_name, receiver)
    with smtplib.SMTP_SSL(setting.SMTP_HOST, setting.SMTP_PORT) as server:
        server.login(setting.SMTP_USER, setting.SMTP_PASSWORD)
        server.send_message(email)
