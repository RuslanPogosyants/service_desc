import unittest
from typing import AsyncGenerator
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.tasks.email_tasks import fetch_emails_task
from app.api.schemas import TicketCreate
from app.mail.client import EmailClient
from app.services import ticket_service
from app.tasks.email_tasks import send_email_task


class TestFetchEmailsTask(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        """
        Настройка тестового окружения.
        """
        self.mock_email_client = AsyncMock(spec=EmailClient)
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.mock_ticket_service = AsyncMock(spec=ticket_service)
        self.mock_send_email_task = MagicMock(spec=send_email_task.delay)

    async def mock_async_generator(self, session) -> AsyncGenerator[AsyncSession, None]:
        """
        Мок для асинхронного генератора.
        """
        yield session

    @patch("app.tasks.email_tasks.email_client", new_callable=MagicMock)
    @patch("app.tasks.email_tasks.get_async_session", new_callable=MagicMock)
    @patch("app.tasks.email_tasks.ticket_service", new_callable=AsyncMock)
    @patch("app.tasks.email_tasks.send_email_task.delay", new_callable=MagicMock)
    async def test_fetch_emails_task_with_new_emails(
        self,
        mock_send_email_task: MagicMock,
        mock_ticket_service: AsyncMock,
        mock_get_async_session: MagicMock,
        mock_email_client: MagicMock,
    ) -> None:
        """
        Тест успешного выполнения задачи с новыми письмами.
        """
        mock_email_client.fetch_emails.return_value = [
            ("test1@example.com", "Test Subject 1", "Test Body 1"),
            ("test2@example.com", "Test Subject 2", "Test Body 2"),
        ]

        mock_get_async_session.return_value = self.mock_async_generator(
            self.mock_session
        )

        await fetch_emails_task()

        mock_email_client.fetch_emails.assert_called_once()

        self.assertEqual(mock_ticket_service.create_ticket.call_count, 2)
        mock_ticket_service.create_ticket.assert_any_call(
            self.mock_session,
            TicketCreate(subject="Test Subject 1", description="Test Body 1"),
        )
        mock_ticket_service.create_ticket.assert_any_call(
            self.mock_session,
            TicketCreate(subject="Test Subject 2", description="Test Body 2"),
        )

        self.assertEqual(mock_send_email_task.call_count, 2)
        mock_send_email_task.assert_any_call(
            "test1@example.com",
            "Re: Test Subject 1",
            "Ваше обращение принято и будет обработано в ближайшее время",
        )
        mock_send_email_task.assert_any_call(
            "test2@example.com",
            "Re: Test Subject 2",
            "Ваше обращение принято и будет обработано в ближайшее время",
        )

    @patch("app.tasks.email_tasks.email_client", new_callable=MagicMock)  # Используем MagicMock
    @patch("app.tasks.email_tasks.get_async_session", new_callable=MagicMock)
    @patch("app.tasks.email_tasks.ticket_service", new_callable=AsyncMock)
    @patch("app.tasks.email_tasks.send_email_task.delay", new_callable=MagicMock)
    async def test_fetch_emails_task_with_no_new_emails(
            self,
            mock_send_email_task: MagicMock,
            mock_ticket_service: AsyncMock,
            mock_get_async_session: MagicMock,
            mock_email_client: MagicMock,
    ) -> None:
        """
        Тест выполнения задачи без новых писем.
        """
        mock_email_client.fetch_emails.return_value = []
        mock_get_async_session.return_value = self.mock_async_generator(
            self.mock_session
        )

        await fetch_emails_task()

        mock_email_client.fetch_emails.assert_called_once()
        mock_ticket_service.create_ticket.assert_not_called()
        mock_send_email_task.assert_not_called()


if __name__ == "__main__":
    unittest.main()