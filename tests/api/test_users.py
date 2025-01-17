import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from fastapi import status
from datetime import datetime
from typing import Any
import asyncio

from app.api.schemas import User, BaseResponse


async def future(value: Any) -> Any:
    """
    Создает asyncio.Future с заданным значением и возвращает его.
    """
    f = asyncio.Future[Any]()
    f.set_result(value)
    return f


@pytest.mark.asyncio
class TestUserCreation:
    @pytest.fixture(autouse=True)
    def setup(self, client: AsyncClient, db_session: AsyncMock) -> None:
        self.client = client
        self.db_session = db_session
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        }
        self.now = datetime.now()
        self.expected_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )

    async def test_create_user_successful(self) -> None:
        """
        Тест проверяет успешное создание пользователя.
        """

        async def mock_create_user(*args, **kwargs) -> User:
            return self.expected_user

        with patch(
            "app.services.user_service.create_user",
            new_callable=AsyncMock,
            side_effect=mock_create_user,
        ) as mock_create_user:
            response = self.client.post("/api/users", json=self.user_data)

        assert response.status_code == status.HTTP_201_CREATED
        mock_create_user.assert_called_once()
        expected_response: BaseResponse = BaseResponse(
            data=self.expected_user, message="Пользователь успешно создан"
        )
        expected_response.data.created_at = (
            expected_response.data.created_at.isoformat()
        )
        expected_response.data.updated_at = (
            expected_response.data.updated_at.isoformat()
        )
        assert response.json() == expected_response.model_dump()

    async def test_create_user_failure_with_duplicate_email(self) -> None:
        """
        Тест проверяет ошибку при создании пользователя с уже существующим email.
        """
        with patch(
            "app.services.user_service.create_user", new_callable=AsyncMock
        ) as mock_create_user:
            mock_create_user.side_effect = ValueError(
                "Почта с таким именем уже зарегистрирована"
            )
            response = self.client.post("/api/users", json=self.user_data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST

            mock_create_user.assert_awaited_once()
            assert response.json() == {
                "detail": "Почта с таким именем уже зарегистрирована"
            }

    async def test_create_user_failure_with_bad_user_data(self) -> None:
        """
        Тест проверяет ошибку при создании пользователя с неверными данными
        """
        bad_user_data = {
            "email": "testexample.com",
            "username": 1,
            "password": "password123",
        }
        response = self.client.post("/api/users", json=bad_user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
