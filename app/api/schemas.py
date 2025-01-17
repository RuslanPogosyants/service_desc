from datetime import datetime
from typing import Optional, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """
    Базовая модель ответа API с данными.
    """

    data: Optional[T] = Field(None, description="Данные ответа")
    message: Optional[str] = Field(None, description="Сообщение об ошибке, или успехе")


class UserCreate(BaseModel):
    """
    Модель для создания пользователя.
    """

    email: str = Field(..., description="Email пользователя")
    username: str = Field(..., description="Логин пользователя")
    password: str = Field(..., description="Пароль пользователя")


class User(BaseModel):
    """
    Модель пользователя для ответа API.
    """

    id: int = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    username: str = Field(..., description="Логин пользователя")
    is_active: bool = Field(..., description="Активен ли пользователь")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class TicketCreate(BaseModel):
    """
    Модель для создания обращения.
    """

    subject: str = Field(..., description="Тема обращения")
    description: str = Field(..., description="Описание обращения")


class TicketUpdate(BaseModel):
    """
    Модель для обновления обращения.
    """

    status: Optional[str] = Field(None, description="Новый статус обращения")
    operator_id: Optional[int] = Field(
        None, description="ID оператора, взявшего обращение"
    )


class Ticket(BaseModel):
    """
    Модель обращения для ответа API.
    """

    id: int = Field(..., description="ID обращения")
    subject: str = Field(..., description="Тема обращения")
    description: str = Field(..., description="Описание обращения")
    status: str = Field(..., description="Статус обращения")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    creator: User = Field(..., description="Пользователь, создавший обращение")
    operator: Optional[User] = Field(None, description="Оператор, взявший обращение")


class MessageCreate(BaseModel):
    """
    Модель для создания сообщения.
    """

    text: str = Field(..., description="Текст сообщения")


class Message(BaseModel):
    """
    Модель сообщения для ответа API.
    """

    id: int = Field(..., description="ID сообщения")
    text: str = Field(..., description="Текст сообщения")
    created_at: datetime = Field(..., description="Дата создания")
    author: User = Field(..., description="Автор сообщения")
