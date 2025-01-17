from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    UserCreate,
    User,
    TicketCreate,
    TicketUpdate,
    Ticket,
    MessageCreate,
    Message,
    BaseResponse,
)
from app.api.enums import SortOrder, TicketStatus
from app.core.database import get_async_session
from app.services import ticket_service, user_service
from app.tasks.email_tasks import send_email_task


router = APIRouter()


@router.post(
    "/users",
    response_model=BaseResponse[User],
    status_code=status.HTTP_201_CREATED,
    description="Создание нового пользователя",
)
async def create_user(
    user_data: UserCreate, session: AsyncSession = Depends(get_async_session)
) -> BaseResponse[User]:
    """Создает нового пользователя"""
    try:
        user = await user_service.create_user(session, user_data)
        return BaseResponse(data=user, message="Пользователь успешно создан")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/users/{user_id}",
    response_model=BaseResponse[User],
    description="Получение пользователя по id",
)
async def get_user(
    user_id: int, session: AsyncSession = Depends(get_async_session)
) -> BaseResponse[User]:
    """Возвращает пользователя по его ID"""
    user = await user_service.get_user(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return BaseResponse(data=user, message="Пользователь успешно получен")


@router.post(
    "/tickets",
    response_model=BaseResponse[Ticket],
    status_code=status.HTTP_201_CREATED,
    description="Создание нового обращения",
)
async def create_ticket(
    ticket_data: TicketCreate, session: AsyncSession = Depends(get_async_session)
) -> BaseResponse[Ticket]:
    """Создает новое обращение"""
    try:
        ticket = await ticket_service.create_ticket(session, ticket_data)
        return BaseResponse(data=ticket, message="Обращение успешно создано")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/tickets",
    response_model=BaseResponse[List[Ticket]],
    description="Получение списка обращений",
)
async def get_tickets(
    status: Optional[TicketStatus] = None,
    sort_by: SortOrder = SortOrder.CREATED_AT_DESC,
    session: AsyncSession = Depends(get_async_session),
) -> BaseResponse[List[Ticket]]:
    """Получение списка обращений, с фильтрацией по статусу и сортировкой"""

    tickets = await ticket_service.get_tickets(session, status, sort_by)
    return BaseResponse(data=tickets, message="Список обращений успешно получен")


@router.get(
    "/tickets/{ticket_id}",
    response_model=BaseResponse[Ticket],
    description="Получение обращения по ID",
)
async def get_ticket(
    ticket_id: int, session: AsyncSession = Depends(get_async_session)
) -> BaseResponse[Ticket]:
    """Получение обращения по ID"""
    ticket = await ticket_service.get_ticket(session, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    return BaseResponse(data=ticket, message="Обращение успешно получено")


@router.patch(
    "/tickets/{ticket_id}",
    response_model=BaseResponse[Ticket],
    description="Обновление обращения",
)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> BaseResponse[Ticket]:
    """Обновление обращения"""
    try:
        ticket = await ticket_service.update_ticket(session, ticket_id, ticket_data)
        return BaseResponse(data=ticket, message="Обращение успешно обновлено")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/tickets/{ticket_id}/messages",
    response_model=BaseResponse[Message],
    status_code=status.HTTP_201_CREATED,
    description="Создание сообщения в обращении",
)
async def create_message(
    ticket_id: int,
    message_data: MessageCreate,
    session: AsyncSession = Depends(get_async_session),
) -> BaseResponse[Message]:
    """Создание сообщения в обращении"""
    try:
        message = await ticket_service.create_message(session, ticket_id, message_data)
        ticket = await ticket_service.get_ticket(session, ticket_id)
        if ticket and ticket.creator:
            send_email_task.delay(
                ticket.creator.email, f"Re: {ticket.subject}", message_data.text
            )
        return BaseResponse(data=message, message="Сообщение успешно создано")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/tickets/{ticket_id}/messages",
    response_model=BaseResponse[List[Message]],
    description="Получение сообщений по обращению",
)
async def get_messages(
    ticket_id: int, session: AsyncSession = Depends(get_async_session)
) -> BaseResponse[List[Message]]:
    """Получение сообщений по обращению"""
    messages = await ticket_service.get_messages(session, ticket_id)
    return BaseResponse(data=messages, message="Список сообщений успешно получен")
