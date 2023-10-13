from flask_mail import Mail, Message

mail = Mail()


def init_mail(app):
    mail.init_app(app)


def send_mail(subject, sender, recipients, text_body=None, html_body=None):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    if text_body:
        msg.body = text_body
    if html_body:
        msg.html = html_body
    mail.send(msg)

