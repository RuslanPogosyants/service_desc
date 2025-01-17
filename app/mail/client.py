import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Tuple
from app.core.config import Settings

settings = Settings()


class EmailClient:
    """
    Клиент для отправки и получения mail сообщений.
    """

    def __init__(self) -> None:
        """
        Инициализация клиента.
        """
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from_email = settings.smtp_from_email
        self.imap_host = settings.email_imap_host
        self.imap_port = settings.email_imap_port
        self.imap_user = settings.email_imap_user
        self.imap_password = settings.email_imap_password

    def send_email(self, to_email: str, subject: str, message: str) -> None:
        msg = MIMEMultipart()
        msg["From"] = self.smtp_from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        try:
            print("Подключение к SMTP серверу...")
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30) as server:
                print("Успешное подключение. Авторизация...")
                server.login(self.smtp_user, self.smtp_password)
                print("Авторизация успешна. Отправка письма...")
                server.send_message(msg)
                print("Письмо отправлено.")
        except Exception as e:
            print(f"Ошибка при отправке mail: {e}")

    def fetch_emails(self) -> List[Tuple[str, str, str]]:
        messages: List[Tuple[str, str, str]] = []
        try:
            with imaplib.IMAP4_SSL(self.imap_host, self.imap_port, timeout=10) as mail:
                mail.login(self.imap_user, self.imap_password)
                mail.select("inbox")

                _, data = mail.search(None, "UNSEEN")
                for num in data[0].split():
                    _, data = mail.fetch(num, "(RFC822)")
                    if isinstance(data, tuple) and isinstance(data[0], bytes):
                        raw_email = data[0][1]
                    else:
                        raise ValueError("Неожиданный тип данных при получении mail")

                    email_message = email.message_from_bytes(raw_email)

                    from_email = str(
                        email.utils.parseaddr(email_message.get("from"))[1]
                    )
                    subject = str(email_message.get("subject"))
                    body = ""

                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break

                    else:
                        body = email_message.get_payload(decode=True).decode()

                    messages.append((from_email, subject, body))

                for num in data[0].split():
                    mail.store(num, "+FLAGS", r"\Seen")

        except Exception as e:
            print(f"Ошибка при получении mail: {e}")

        return messages
