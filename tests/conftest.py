from typing import Any, AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from app.main import app
from app.core.config import Settings
from app.database.models import Base

settings = Settings()

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Фикстура для создания тестового клиента FastAPI.
    """
    return TestClient(app)


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Фикстура для создания тестового движка БД.
    """
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, Any]:
    """
    Фикстура для создания сессии базы данных.
    """
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
