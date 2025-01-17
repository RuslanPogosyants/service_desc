import unittest
from unittest.mock import patch, MagicMock
import smtplib
from app.mail.client import EmailClient
from app.core.config import Settings


class TestEmailClient(unittest.TestCase):
    def setUp(self) -> None:
        """
        Настройка тестового окружения.
        """
        self.settings = Settings()
        self.email_client = EmailClient()

    @patch("smtplib.SMTP_SSL")
    def test_send_email_success(self, mock_smtp_ssl: MagicMock) -> None:
        """
        Тест успешной отправки письма.
        """
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        self.email_client.send_email("test@example.com", "Test Subject", "Test Message")

        mock_smtp_ssl.assert_called_once_with(
            self.settings.smtp_host, self.settings.smtp_port, timeout=30
        )

        mock_server.login.assert_called_once_with(
            self.settings.smtp_user, self.settings.smtp_password
        )
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP_SSL")
    def test_send_email_failure(self, mock_smtp_ssl: MagicMock) -> None:
        """
        Тест ошибки при отправке письма.
        """
        mock_smtp_ssl.side_effect = smtplib.SMTPException("SMTP Error")

        self.email_client.send_email("test@example.com", "Test Subject", "Test Message")

        mock_smtp_ssl.assert_any_call(
            self.settings.smtp_host, self.settings.smtp_port, timeout=30
        )


if __name__ == "__main__":
    unittest.main()
