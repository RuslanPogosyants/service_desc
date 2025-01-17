import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из переменных окружения.
    """

    model_config = SettingsConfigDict(env_file="../../.env", env_file_encoding="utf-8")

    app_name: str = Field("Service Desk", description="Название приложения")
    environment: str = Field("development", description="Окружение приложения")
    database_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/service_desk_db"
        if os.getenv("environment") == "development"
        else f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}",
        description="URL для подключения к базе данных PostgreSQL",
    )
    smtp_host: str = Field(description="SMTP хост")
    smtp_port: int = Field(description="SMTP порт")
    smtp_user: str = Field(description="SMTP пользователь")
    smtp_password: str = Field(description="SMTP пароль")
    smtp_from_email: str = Field(description="Email отправителя")
    email_imap_host: str = Field(description="IMAP хост")
    email_imap_port: int = Field(description="IMAP порт")
    email_imap_user: str = Field(description="IMAP пользователь")
    email_imap_password: str = Field(description="IMAP пароль")
    redis_host: str = Field(description="Redis host")
    redis_port: int = Field(description="Redis port")
    POSTGRES_USER: str = Field(description="Postgres user")
    POSTGRES_PASSWORD: str = Field(description="Postgres password")
    POSTGRES_DB: str = Field(description="Postgres db name")
