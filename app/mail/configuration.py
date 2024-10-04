from flask import Flask
from flask_mail import Mail, Message


class MailSender:
    _mail = None
    _sender = None

    def __init__(self, app: Flask, sender: str) -> None:
        MailSender._mail = Mail(app)
        MailSender._sender = sender

    @classmethod
    def send(cls, email: str, subject: str, content: str) -> None:
        mail_content = f'''
                    <html>
                        <body>
                            <div style="font-family:Consolas;margin:auto 100px;padding:5px;text-size:16px;color:white;background-color:grey">
                                {content}
                            </div>
                        </body>
                    </html>
                '''

        message = Message(
            subject=subject,
            sender=cls._sender,
            recipients=[email],
            html=mail_content,
        )
        cls._mail.send(message)
