from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Модель пользователя системы.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="creator", foreign_keys="Ticket.creator_id"
    )
    operator_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="operator", foreign_keys="Ticket.operator_id"
    )


class Ticket(Base):
    """
    Модель обращения (тикета).
    """

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String, default="open"
    )  # Статус: open, in_progress, closed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    creator: Mapped["User"] = relationship(
        "User", back_populates="tickets", foreign_keys=[creator_id]
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    operator: Mapped[Optional["User"]] = relationship(
        "User", back_populates="operator_tickets", foreign_keys=[operator_id]
    )
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="ticket")


class Message(Base):
    """
    Модель сообщения в тикете.
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"))
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="messages")
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id])
