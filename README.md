# Service Desk

## Описание

Этот проект представляет собой API для системы управления обращениями (Service Desk). Он позволяет создавать, просматривать, обновлять и комментировать обращения, а также управлять пользователями. API разработан на основе FastAPI и использует SQLAlchemy для работы с базой данных PostgreSQL, Celery для асинхронных задач, Redis в качестве брокера и бэкэнда Celery, и Pydantic для валидации данных. Также предусмотрен Email клиент для получения и отправки писем.

## Технологии

*   **FastAPI**: Современный, высокопроизводительный фреймворк для создания API на Python.
*   **SQLAlchemy**: ORM (Object-Relational Mapper) для работы с базой данных.
*   **PostgreSQL**: Реляционная база данных.
*   **Celery**: Распределенная система для асинхронных задач.
*   **Redis**: In-memory база данных, используется как брокер сообщений Celery и бэкенд.
*   **Pydantic**: Библиотека для валидации и преобразования данных.
*   **Alembic**: Для управления миграциями базы данных.
*   **MyPy**: Статический анализатор типов Python.
---
## Установка

1.  **Клонирование репозитория:**

    ```bash
    git clone https://github.com/service_desc.git
    cd <название_репозитория>
    ```

2.  **Создание виртуального окружения (рекомендуется):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Linux/macOS
    venv\Scripts\activate   # Для Windows
    ```

3.  **Установка зависимостей:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Создание файла `.env`:**
Создайте файл .env в корне проекта и заполните его по примеру:
```
app_name="Service Desk"
environment="development"
database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/service_desk_db"
smtp_host="smtp.example.com"
smtp_port=587
smtp_user="your-email@example.com"
smtp_password="your-password"
smtp_from_email="your-email@example.com"
email_imap_host="imap.example.com"
email_imap_port=993
email_imap_user="your-email@example.com"
email_imap_password="your-password"
redis_host="redis"
redis_port=6379

POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
POSTGRES_DB="service_desk_db"
```
---
## Запуск приложения

1.  **Запуск сервера FastAPI:**

    ```bash
    uvicorn app.main:app --reload
    ```
    Это запустит сервер FastAPI с горячей перезагрузкой.

    *   **Примечание:** Этот вариант не запускает базу данных, Redis и Celery. Вам нужно будет запустить их отдельно, если вы будете использовать этот метод.

2.  **Запуск Celery worker:**

     ```bash
        celery -A app.tasks.email_tasks worker --loglevel=INFO
     ```
     Это запустит Celery воркер, который будет выполнять асинхронные задачи. (В отдельной консоли)

## Запуск миграций БД

1. **Установка Alembic**

    ```bash
    pip install alembic
    ```
2.  **Создание миграции:**

    ```bash
    alembic revision -m "Initial migration"
    ```

3.  **Применение миграций:**

    ```bash
    alembic upgrade head
    ```

---
## API

API документация доступна через Swagger:

-   **Swagger**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

### Основные эндпоинты:

#### Пользователи

*   **Создание пользователя:**
    *   **URL:** `POST /api/users`
    *   **Описание:** Создает нового пользователя.
    *   **Тело запроса (JSON):**

        ```json
        {
            "email": "user@example.com",
            "username": "newuser",
            "password": "secure_password"
        }
        ```

    *   **Ответ (JSON) 201:**
        ```json
        {
            "data": {
               "id": 1,
                "email": "user@example.com",
                "username": "newuser",
                "is_active": true,
                "created_at": "2025-01-14T13:32:48.417565",
                "updated_at": "2025-01-14T13:32:48.417565"
            },
            "message": "Пользователь успешно создан"
        }
        ```
     *   **Ответ (JSON) 400:**
       ```json
       {
          "detail": "Почта с таким именем ужё зарегистрирована"
       }
      ```

*   **Получение пользователя по ID:**
    *   **URL:** `GET /api/users/{user_id}`
    *   **Описание:** Возвращает пользователя по его ID.
    *   **Параметры пути:**
        *   `user_id`: ID пользователя (целое число).
    *   **Ответ (JSON) 200:**
        ```json
        {
            "data": {
                 "id": 1,
                "email": "user@example.com",
                "username": "newuser",
                "is_active": true,
                "created_at": "2025-01-14T13:32:48.417565",
                "updated_at": "2025-01-14T13:32:48.417565"
            },
            "message": "Пользователь успешно получен"
        }
        ```
    *   **Ответ (JSON) 404:**
          ```json
          {
               "detail": "User not found"
           }
          ```

#### Тикеты

*   **Создание обращения:**
    *   **URL:** `POST /api/tickets`
    *   **Описание:** Создает новое обращение.
    *  **Тело запроса (JSON):**

        ```json
        {
            "subject": "Проблема с принтером",
            "description": "Принтер не печатает, пожалуйста помогите."
        }
        ```

    *   **Ответ (JSON) 201:**
        ```json
        {
           "data": {
               "id": 1,
               "subject": "Проблема с принтером",
               "description": "Принтер не печатает, пожалуйста помогите.",
               "status": "open",
               "created_at": "2025-01-14T13:32:48.417565",
                "updated_at": "2025-01-14T13:32:48.417565",
               "creator": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "newuser",
                    "is_active": true,
                    "created_at": "2025-01-14T13:32:48.417565",
                    "updated_at": "2025-01-14T13:32:48.417565"
                },
                "operator": null
            },
            "message": "Обращение успешно создано"
        }
        ```
        *    **Ответ (JSON) 400:**
          ```json
          {
              "detail": "Пользователь c ID {creator_id} не найден"
          }
          ```
*   **Получение списка обращений:**
    *   **URL:** `GET /api/tickets`
    *   **Описание:** Возвращает список обращений.
    *   **Параметры запроса:**
        *   `status` (опционально): Фильтр по статусу обращения (`open`, `in_progress`, `closed`).
        *   `sort_by` (опционально): Сортировка по времени создания (`created_at_asc`, `created_at_desc`). По умолчанию `created_at_desc`.
    *   **Ответ (JSON) 200:**
          ```json
            {
                "data": [
                    {
                       "id": 1,
                       "subject": "Проблема с принтером",
                       "description": "Принтер не печатает, пожалуйста помогите.",
                       "status": "open",
                       "created_at": "2025-01-14T13:32:48.417565",
                        "updated_at": "2025-01-14T13:32:48.417565",
                       "creator": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "newuser",
                             "is_active": true,
                             "created_at": "2025-01-14T13:32:48.417565",
                            "updated_at": "2025-01-14T13:32:48.417565"
                        },
                       "operator": null
                   }
               ],
                "message": "Список обращений успешно получен"
             }
           ```

*   **Получение обращения по ID:**
    *   **URL:** `GET /api/tickets/{ticket_id}`
    *   **Описание:** Возвращает обращение по его ID.
    *   **Параметры пути:**
        *   `ticket_id`: ID обращения (целое число).
    *   **Ответ (JSON) 200:**

          ```json
           {
                "data": {
                   "id": 1,
                       "subject": "Проблема с принтером",
                       "description": "Принтер не печатает, пожалуйста помогите.",
                       "status": "open",
                       "created_at": "2025-01-14T13:32:48.417565",
                        "updated_at": "2025-01-14T13:32:48.417565",
                       "creator": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "newuser",
                            "is_active": true,
                            "created_at": "2025-01-14T13:32:48.417565",
                            "updated_at": "2025-01-14T13:32:48.417565"
                           },
                       "operator": null
                   },
                "message": "Обращение успешно получено"
           }
          ```
    *   **Ответ (JSON) 404:**
            ```json
              {
                "detail": "Ticket not found"
              }
             ```

*   **Обновление обращения:**
    *   **URL:** `PATCH /api/tickets/{ticket_id}`
    *   **Описание:** Обновляет обращение по его ID.
    *   **Параметры пути:**
        *   `ticket_id`: ID обращения (целое число).
    *    **Тело запроса (JSON):**
            ```json
           {
                "status": "in_progress",
                 "operator_id": 1
            }
           ```
    *   **Ответ (JSON) 200:**
        ```json
          {
             "data": {
                "id": 1,
                "subject": "Проблема с принтером",
                "description": "Принтер не печатает, пожалуйста помогите.",
                 "status": "in_progress",
                 "created_at": "2025-01-14T13:32:48.417565",
                 "updated_at": "2025-01-14T13:32:48.417565",
                 "creator": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "newuser",
                            "is_active": true,
                             "created_at": "2025-01-14T13:32:48.417565",
                            "updated_at": "2025-01-14T13:32:48.417565"
                         },
                 "operator": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "newuser",
                            "is_active": true,
                             "created_at": "2025-01-14T13:32:48.417565",
                            "updated_at": "2025-01-14T13:32:48.417565"
                          }
            },
             "message": "Обращение успешно обновлено"
          }
        ```
      *    **Ответ (JSON) 400:**
           ```json
           {
             "detail": "Тикет с id {ticket_id} не найден"
            }
           ```

#### Сообщения

*   **Создание сообщения в обращении:**
    *   **URL:** `POST /api/tickets/{ticket_id}/messages`
    *   **Описание:** Создает новое сообщение в обращении.
    *   **Параметры пути:**
        *   `ticket_id`: ID обращения (целое число).
     *   **Тело запроса (JSON):**
             ```json
             {
                  "text": "Проблема решается."
              }
            ```
    *   **Ответ (JSON) 201:**
        ```json
        {
           "data": {
              "id": 1,
              "text": "Проблема решается.",
              "created_at": "2025-01-14T13:32:48.417565",
                "author": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "newuser",
                    "is_active": true,
                    "created_at": "2025-01-14T13:32:48.417565",
                    "updated_at": "2025-01-14T13:32:48.417565"
                   }
             },
           "message": "Сообщение успешно создано"
          }
        ```
         *   **Ответ (JSON) 400:**
           ```json
           {
              "detail": "Тикет с {ticket_id} не найден"
            }
          ```
*   **Получение сообщений по обращению:**
    *   **URL:** `GET /api/tickets/{ticket_id}/messages`
    *   **Описание:** Возвращает список сообщений для обращения.
    *   **Параметры пути:**
        *   `ticket_id`: ID обращения (целое число).
    *   **Ответ (JSON) 200:**
        ```json
        {
            "data": [
               {
                  "id": 1,
                 "text": "Проблема решается.",
                  "created_at": "2025-01-14T13:32:48.417565",
                  "author": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "newuser",
                            "is_active": true,
                            "created_at": "2025-01-14T13:32:48.417565",
                            "updated_at": "2025-01-14T13:32:48.417565"
                        }
                }
            ],
            "message": "Список сообщений успешно получен"
       }

### Работа с email

- Пользователи могут отправлять обращения на email, указанный в настройках SMTP.
- Операторы могут отвечать на обращения через API, и пользователи получают ответы на email.

---

