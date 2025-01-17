from celery import Celery
from app.core.config import Settings
from app.mail.client import EmailClient
from app.api.schemas import TicketCreate
from app.services import ticket_service
from app.core.database import get_async_session

settings = Settings()

celery: Celery = Celery(
    "email_tasks",
    broker=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/0",
)

email_client = EmailClient()


@celery.task
def send_email_task(to_email: str, subject: str, message: str) -> None:
    """
    Асинхронная задача для отправки mail сообщений.
    """
    email_client.send_email(to_email, subject, message)


@celery.task
async def fetch_emails_task() -> None:
    """Асинхронная задача для получения mail сообщений"""
    new_emails = email_client.fetch_emails()
    if not new_emails:
        return
    async for session in get_async_session():
        for from_email, subject, body in new_emails:
            ticket_data = TicketCreate(subject=subject, description=body)
            await ticket_service.create_ticket(session, ticket_data)
            send_email_task.delay(
                from_email,
                "Re: " + subject,
                "Ваше обращение принято и будет обработано в ближайшее время",
            )
            print("Создана заявка по почте:", from_email)
