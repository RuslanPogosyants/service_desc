import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.api.schemas import UserCreate, User as UserSchema
from app.database.models import User
from app.services.user_service import create_user


class TestUserService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        """
        Настройка тестового окружения.
        """
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.mock_user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

    async def test_create_user_success(self) -> None:
        """
        Тест успешного создания пользователя.
        """
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.is_active = True
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()
        mock_user.hashed_password = "hashed_password"

        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = mock_user

        with patch("app.services.user_service.map_db_model_to_dict") as mock_map:
            mock_map.return_value = {
                "id": 1,
                "email": "test@example.com",
                "username": "testuser",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            result = await create_user(self.mock_session, self.mock_user_data)

            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called_once()
            self.mock_session.refresh.assert_called_once()

            self.assertIsInstance(result, UserSchema)
            self.assertEqual(result.email, "test@example.com")
            self.assertEqual(result.username, "testuser")
            self.assertEqual(result.is_active, True)

    async def test_create_user_duplicate_email(self) -> None:
        """
        Тест ошибки при создании пользователя с дублирующимся email.
        """
        self.mock_session.commit.side_effect = IntegrityError("Ошибка базы данных", {}, Exception())
        with self.assertRaises(ValueError) as context:
            await create_user(self.mock_session, self.mock_user_data)

        self.assertEqual(
            str(context.exception), "Почта с таким именем уже зарегистрирована"
        )

    async def test_create_user_invalid_data(self) -> None:
        """
        Тест ошибки при создании пользователя с некорректными данными.
        """
        invalid_user_data = UserCreate(
            email="",
            username="",
            password="password123",
        )

        with self.assertRaises(ValueError) as context:
            await create_user(self.mock_session, invalid_user_data)

        self.assertIn("Некорректные данные", str(context.exception))

    async def test_create_user_sql_error(self) -> None:
        """
        Тест ошибки при выполнении SQL-запроса.
        """
        self.mock_session.commit.side_effect = Exception("SQL Error")

        with self.assertRaises(Exception) as context:
            await create_user(self.mock_session, self.mock_user_data)

        self.assertEqual(str(context.exception), "SQL Error")


if __name__ == "__main__":
    unittest.main()
