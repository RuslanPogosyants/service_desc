from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import (
    TicketCreate,
    Ticket as TicketSchema,
    User as UserSchema,
    TicketUpdate,
    MessageCreate,
    Message as MessageSchema,
)
from app.api.enums import TicketStatus, SortOrder
import unittest
from sqlalchemy.exc import IntegrityError
from app.services.ticket_service import (
    create_ticket,
    get_tickets,
    get_ticket,
    update_ticket,
    create_message,
    get_messages,
)


class TestTicketService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.mock_ticket_data = TicketCreate(
            subject="Test Subject", description="Test Description"
        )
        self.mock_user = MagicMock()
        self.mock_user.id = 1
        self.mock_user.username = "testuser"
        self.mock_user.email = "test@example.com"
        self.mock_user.is_active = True
        self.mock_user.created_at = datetime.utcnow()
        self.mock_user.updated_at = datetime.utcnow()

    async def test_create_ticket_success(self) -> None:
        """
        Тест успешного создания тикета.
        """
        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            # Мок пользователя как объекта UserSchema
            mock_get_user.return_value = UserSchema(
                id=1,
                username="testuser",
                email="test@example.com",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # Мок объекта Ticket
            mock_ticket = MagicMock()
            mock_ticket.id = 1
            mock_ticket.subject = "Test Subject"
            mock_ticket.description = "Test Description"
            mock_ticket.status = TicketStatus.OPEN.value
            mock_ticket.created_at = datetime.utcnow()
            mock_ticket.updated_at = datetime.utcnow()
            mock_ticket.creator_id = 1

            # Мок функции map_db_model_to_dict
            with patch(
                "app.services.ticket_service.map_db_model_to_dict"
            ) as mock_map_db_model_to_dict:
                mock_map_db_model_to_dict.return_value = {
                    "id": mock_ticket.id,
                    "subject": mock_ticket.subject,
                    "description": mock_ticket.description,
                    "status": mock_ticket.status,
                    "created_at": mock_ticket.created_at.isoformat(),
                    "updated_at": mock_ticket.updated_at.isoformat(),
                    "creator_id": mock_ticket.creator_id,
                }

                result = await create_ticket(
                    self.mock_session, self.mock_ticket_data, creator_id=1
                )

                self.mock_session.add.assert_called_once()
                self.mock_session.commit.assert_called_once()
                self.mock_session.refresh.assert_called_once()

                self.assertIsInstance(result, TicketSchema)
                self.assertEqual(result.subject, "Test Subject")
                self.assertEqual(result.description, "Test Description")
                self.assertEqual(result.status, TicketStatus.OPEN.value)
                self.assertEqual(result.creator.id, 1)
                self.assertEqual(result.creator.username, "testuser")

    async def test_create_ticket_invalid_data(self) -> None:
        """
        Тест создания тикета с невалидными данными.
        """
        invalid_ticket_data = TicketCreate(subject="", description="Test Description")

        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = UserSchema(
                id=1,
                username="testuser",
                email="test@example.com",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            with self.assertRaises(ValueError) as context:
                await create_ticket(
                    self.mock_session, invalid_ticket_data, creator_id=1
                )

            self.assertEqual(str(context.exception), "Некорректные данные")

    async def test_create_ticket_user_not_found(self) -> None:
        """
        Тест создания тикета с несуществующим пользователем.
        """
        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = None

            with self.assertRaises(ValueError) as context:
                await create_ticket(
                    self.mock_session, self.mock_ticket_data, creator_id=999
                )

            self.assertEqual(str(context.exception), "Пользователь c ID 999 не найден")

    async def test_create_ticket_database_error(self) -> None:
        """
        Тест создания тикета с ошибкой при сохранении в базу данных.
        """
        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = UserSchema(
                id=1,
                username="testuser",
                email="test@example.com",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # Мок ошибки при сохранении в базу данных
            self.mock_session.commit.side_effect = IntegrityError(
                "Ошибка базы данных", {}, Exception()
            )

            # Проверка исключения
            with self.assertRaises(IntegrityError) as context:
                await create_ticket(
                    self.mock_session, self.mock_ticket_data, creator_id=1
                )

            self.assertIn("Ошибка базы данных", str(context.exception))

    async def test_create_ticket_default_creator_id(self) -> None:
        """
        Тест создания тикета с использованием значения по умолчанию для creator_id.
        """
        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = UserSchema(
                id=1,
                username="testuser",
                email="test@example.com",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            mock_ticket = MagicMock()
            mock_ticket.id = 1
            mock_ticket.subject = "Test Subject"
            mock_ticket.description = "Test Description"
            mock_ticket.status = TicketStatus.OPEN.value
            mock_ticket.created_at = datetime.utcnow()
            mock_ticket.updated_at = datetime.utcnow()
            mock_ticket.creator_id = 1

            with patch(
                "app.services.ticket_service.map_db_model_to_dict"
            ) as mock_map_db_model_to_dict:
                mock_map_db_model_to_dict.return_value = {
                    "id": mock_ticket.id,
                    "subject": mock_ticket.subject,
                    "description": mock_ticket.description,
                    "status": mock_ticket.status,
                    "created_at": mock_ticket.created_at.isoformat(),
                    "updated_at": mock_ticket.updated_at.isoformat(),
                    "creator_id": mock_ticket.creator_id,
                }

                result = await create_ticket(self.mock_session, self.mock_ticket_data)

                self.assertIsInstance(result, TicketSchema)
                self.assertEqual(result.subject, "Test Subject")
                self.assertEqual(result.creator.id, 1)

    async def test_create_ticket_empty_subject_or_description(self) -> None:
        """
        Тест создания тикета с пустым subject или description.
        """
        invalid_ticket_data = TicketCreate(
            subject="",  # Пустое поле
            description="Test Description",
        )

        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = UserSchema(
                id=1,
                username="testuser",
                email="test@example.com",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            with self.assertRaises(ValueError) as context:
                await create_ticket(
                    self.mock_session, invalid_ticket_data, creator_id=1
                )

            self.assertEqual(str(context.exception), "Некорректные данные")

        invalid_ticket_data = TicketCreate(
            subject="Test Subject",
            description="",  # Пустое поле
        )

        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = UserSchema(
                id=1,
                username="testuser",
                email="test@example.com",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            with self.assertRaises(ValueError) as context:
                await create_ticket(
                    self.mock_session, invalid_ticket_data, creator_id=1
                )

            self.assertEqual(str(context.exception), "Некорректные данные")

    async def test_get_tickets(self) -> None:
        """
        Тест получения списка тикетов с фильтрацией и сортировкой.
        """
        mock_ticket = MagicMock()
        mock_ticket.id = 1
        mock_ticket.subject = "Test Subject"
        mock_ticket.description = "Test Description"
        mock_ticket.status = TicketStatus.OPEN.value
        mock_ticket.created_at = datetime.utcnow()
        mock_ticket.updated_at = datetime.utcnow()
        mock_ticket.creator_id = 1
        mock_ticket.operator_id = None

        mock_user = UserSchema(
            id=1,
            username="testuser",
            email="test@example.com",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_ticket]

        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            self.mock_session.execute.return_value = mock_result

            result = await get_tickets(
                self.mock_session,
                status=TicketStatus.OPEN,
                sort_by=SortOrder.CREATED_AT_DESC,
            )

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], TicketSchema)
            self.assertEqual(result[0].subject, "Test Subject")
            self.assertEqual(result[0].status, TicketStatus.OPEN.value)
            self.assertEqual(result[0].creator.id, 1)
            self.assertEqual(result[0].creator.username, "testuser")

    async def test_get_ticket_success(self) -> None:
        """
        Тест успешного получения тикета по ID.
        """
        mock_ticket = MagicMock()
        mock_ticket.id = 1
        mock_ticket.subject = "Test Subject"
        mock_ticket.description = "Test Description"
        mock_ticket.status = TicketStatus.OPEN.value
        mock_ticket.created_at = datetime.utcnow()
        mock_ticket.updated_at = datetime.utcnow()
        mock_ticket.creator_id = 1
        mock_ticket.operator_id = None

        mock_user = UserSchema(
            id=1,
            username="testuser",
            email="test@example.com",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_ticket

        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            self.mock_session.execute.return_value = mock_result

            result = await get_ticket(self.mock_session, ticket_id=1)

            self.assertIsInstance(result, TicketSchema)
            self.assertEqual(result.subject, "Test Subject")
            self.assertEqual(result.creator.id, 1)
            self.assertEqual(result.creator.username, "testuser")

    async def test_get_ticket_not_found(self) -> None:
        """
        Тест получения тикета, если он не найден.
        """
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        self.mock_session.execute.return_value = mock_result
        result = await get_ticket(self.mock_session, ticket_id=1)
        self.assertIsNone(result)

    async def test_update_ticket_success(self) -> None:
        """
        Тест успешного обновления тикета.
        """
        mock_ticket = MagicMock()
        mock_ticket.id = 1
        mock_ticket.subject = "Old Subject"
        mock_ticket.description = "Old Description"
        mock_ticket.status = TicketStatus.OPEN.value
        mock_ticket.created_at = datetime.utcnow()
        mock_ticket.updated_at = datetime.utcnow()
        mock_ticket.creator_id = 1
        mock_ticket.operator_id = None

        mock_user = UserSchema(
            id=1,
            username="testuser",
            email="test@example.com",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_ticket

        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            self.mock_session.execute.return_value = mock_result

            update_data = TicketUpdate(status=TicketStatus.CLOSED.value)

            result = await update_ticket(
                self.mock_session, ticket_id=1, ticket_data=update_data
            )

            self.assertIsInstance(result, TicketSchema)
            self.assertEqual(result.status, TicketStatus.CLOSED.value)

    async def test_update_ticket_not_found(self) -> None:
        """
        Тест обновления тикета, если он не найден.
        """
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        self.mock_session.execute.return_value = mock_result

        update_data = TicketUpdate(status=TicketStatus.CLOSED.value)

        with self.assertRaises(ValueError) as context:
            await update_ticket(self.mock_session, ticket_id=1, ticket_data=update_data)

        self.assertEqual(str(context.exception), "Тикет с id 1 не найден")

    async def test_create_message_success(self) -> None:
        """
        Тест успешного создания сообщения.
        """
        mock_ticket = MagicMock()
        mock_ticket.id = 1
        mock_ticket.subject = "Test Subject"
        mock_ticket.description = "Test Description"
        mock_ticket.status = TicketStatus.OPEN.value
        mock_ticket.created_at = datetime.utcnow()
        mock_ticket.updated_at = datetime.utcnow()
        mock_ticket.creator_id = 1
        mock_ticket.operator_id = None

        mock_message = MagicMock()
        mock_message.id = 1
        mock_message.text = "Test Message"
        mock_message.ticket_id = 1
        mock_message.author_id = 1
        mock_message.created_at = datetime.utcnow()

        mock_user = UserSchema(
            id=1,
            username="testuser",
            email="test@example.com",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_ticket_result = MagicMock()
        mock_ticket_result.scalar_one_or_none.return_value = mock_ticket

        mock_message_result = MagicMock()
        mock_message_result.scalar_one.return_value = mock_message

        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            self.mock_session.execute.side_effect = [
                mock_ticket_result,
                mock_message_result,
            ]

            self.mock_session.commit.return_value = None
            self.mock_session.refresh.return_value = None

            message_data = MessageCreate(text="Test Message")

            result = await create_message(
                self.mock_session, ticket_id=1, message_data=message_data, author_id=1
            )

            self.assertIsInstance(result, MessageSchema)
            self.assertEqual(result.text, "Test Message")
            self.assertEqual(result.author.id, 1)
            self.assertEqual(result.author.username, "testuser")

    async def test_create_message_ticket_not_found(self) -> None:
        """
        Тест создания сообщения, если тикет не найден.
        """
        mock_ticket_result = MagicMock()
        mock_ticket_result.scalar_one_or_none.return_value = None

        self.mock_session.execute.return_value = mock_ticket_result
        message_data = MessageCreate(text="Test Message")

        with self.assertRaises(ValueError) as context:
            await create_message(
                self.mock_session, ticket_id=1, message_data=message_data, author_id=1
            )

        self.assertEqual(str(context.exception), "Тикет с 1 не найден")

    async def test_get_messages(self) -> None:
        """
        Тест получения списка сообщений по ID тикета.
        """
        mock_message = MagicMock()
        mock_message.id = 1
        mock_message.text = "Test Message"
        mock_message.ticket_id = 1
        mock_message.author_id = 1
        mock_message.created_at = datetime.utcnow()

        mock_user = UserSchema(
            id=1,
            username="testuser",
            email="test@example.com",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_message]

        with patch(
            "app.services.user_service.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            self.mock_session.execute.return_value = mock_result
            result = await get_messages(self.mock_session, ticket_id=1)

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], MessageSchema)
            self.assertEqual(result[0].text, "Test Message")
            self.assertEqual(result[0].author.id, 1)
            self.assertEqual(result[0].author.username, "testuser")


if __name__ == "__main__":
    unittest.main()
