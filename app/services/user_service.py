from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from app.api.schemas import UserCreate, User as UserSchema
from app.database.models import User
from app.core.config import Settings
from app.database.tools import map_db_model_to_dict

# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = Settings()


async def create_user(session: AsyncSession, user_data: UserCreate) -> UserSchema:
    """
    Создает нового пользователя в базе данных.
    """
    try:
        if not user_data.email or not user_data.username:
            raise ValueError("Некорректные данные")
        hashed_password = pwd_context.hash(user_data.password)
        user = User(
            **user_data.model_dump(exclude={"password"}),
            hashed_password=hashed_password,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserSchema.model_validate(map_db_model_to_dict(user))
    except IntegrityError:
        raise ValueError("Почта с таким именем уже зарегистрирована")


async def get_user(
    session: AsyncSession, user_id: Optional[int]
) -> Optional[UserSchema]:
    """
    Получает пользователя из базы данных по ID.
    """
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        return UserSchema.model_validate(map_db_model_to_dict(user))
    return None
