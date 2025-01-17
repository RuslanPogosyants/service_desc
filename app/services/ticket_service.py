from typing import List, Optional

from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from app.api.schemas import (
    TicketCreate,
    TicketUpdate,
    MessageCreate,
    Message as MessageSchema,
    Ticket as TicketSchema,
)
from app.api.enums import SortOrder, TicketStatus
from app.database.models import Ticket, Message
from app.core.config import Settings
from app.services import user_service
from app.database.tools import map_db_model_to_dict

settings = Settings()


async def create_ticket(
    session: AsyncSession, ticket_data: TicketCreate, creator_id: int = 1
) -> TicketSchema:
    """
    Создает новое обращение.
    """
    if not ticket_data.subject or not ticket_data.description:
        raise ValueError("Некорректные данные")

    user = await user_service.get_user(session, creator_id)
    if not user:
        raise ValueError(f"Пользователь c ID {creator_id} не найден")
    ticket = Ticket(**ticket_data.model_dump(), creator_id=creator_id)
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    ticket_dict = map_db_model_to_dict(ticket)
    ticket_dict["creator"] = user
    return TicketSchema.model_validate(ticket_dict)


async def get_tickets(
    session: AsyncSession,
    status: Optional[TicketStatus] = None,
    sort_by: SortOrder = SortOrder.CREATED_AT_DESC,
) -> List[TicketSchema]:
    """
    Получает список обращений с возможностью фильтрации по статусу и сортировки.
    """
    stmt = select(Ticket).options(
        selectinload(Ticket.creator), selectinload(Ticket.operator)
    )
    if status:
        stmt = stmt.where(Ticket.status == status.value)

    if sort_by == SortOrder.CREATED_AT_ASC:
        stmt = stmt.order_by(desc(Ticket.created_at))
    elif sort_by == SortOrder.CREATED_AT_DESC:
        stmt = stmt.order_by(asc(Ticket.created_at))

    result = await session.execute(stmt)
    tickets = result.scalars().all()

    result_tickets = []
    for ticket in tickets:
        ticket_dict = map_db_model_to_dict(ticket)
        if ticket.creator:
            ticket_dict["creator"] = await user_service.get_user(
                session, ticket.creator_id
            )
        if ticket.operator:
            ticket_dict["operator"] = await user_service.get_user(
                session, ticket.operator_id
            )
        result_tickets.append(TicketSchema.model_validate(ticket_dict))
    return result_tickets


async def get_ticket(session: AsyncSession, ticket_id: int) -> Optional[TicketSchema]:
    """
    Получает обращение по ID.
    """
    stmt = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.creator), selectinload(Ticket.operator))
    )
    result = await session.execute(stmt)
    ticket = result.scalar_one_or_none()
    if ticket:
        ticket_dict = map_db_model_to_dict(ticket)
        if ticket.creator:
            ticket_dict["creator"] = await user_service.get_user(
                session, ticket.creator_id
            )
        if ticket.operator:
            ticket_dict["operator"] = await user_service.get_user(
                session, ticket.operator_id
            )
        return TicketSchema.model_validate(ticket_dict)
    return None


async def update_ticket(
    session: AsyncSession, ticket_id: int, ticket_data: TicketUpdate
) -> Optional[TicketSchema]:
    """
    Обновляет обращение по ID.
    """
    stmt = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.creator), selectinload(Ticket.operator))
    )
    result = await session.execute(
        stmt
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise ValueError(f"Тикет с id {ticket_id} не найден")

    for key, value in ticket_data.model_dump(exclude_unset=True).items():
        setattr(ticket, key, value)

    await session.commit()
    await session.refresh(ticket)

    ticket_dict = map_db_model_to_dict(ticket)
    if ticket.creator:
        ticket_dict["creator"] = await user_service.get_user(session, ticket.creator_id)
    if ticket.operator:
        ticket_dict["operator"] = await user_service.get_user(
            session, ticket.operator_id
        )

    return TicketSchema.model_validate(ticket_dict)


async def create_message(
    session: AsyncSession,
    ticket_id: int,
    message_data: MessageCreate,
    author_id: int = 1,
) -> MessageSchema:
    """
    Создает сообщение в обращении.
    """
    ticket = await get_ticket(session, ticket_id)
    if not ticket:
        raise ValueError(f"Тикет с {ticket_id} не найден")

    message = Message(
        **message_data.model_dump(), ticket_id=ticket_id, author_id=author_id
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)

    stmt = (
        select(Message)
        .where(Message.id == message.id)
        .options(selectinload(Message.author))
    )
    result = await session.execute(stmt)
    message_db = result.scalar_one()

    message_dict = map_db_model_to_dict(message_db)
    if message_db.author:
        message_dict["author"] = await user_service.get_user(
            session, message_db.author_id
        )

    return MessageSchema.model_validate(message_dict)


async def get_messages(session: AsyncSession, ticket_id: int) -> List[MessageSchema]:
    """
    Получает список сообщений по ID обращения.
    """
    stmt = (
        select(Message)
        .where(Message.ticket_id == ticket_id)
        .options(selectinload(Message.author))
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()
    result_messages = []
    for message in messages:
        message_dict = map_db_model_to_dict(message)
        if message.author:
            message_dict["author"] = await user_service.get_user(
                session, message.author_id
            )
        result_messages.append(MessageSchema.model_validate(message_dict))
    return result_messages
