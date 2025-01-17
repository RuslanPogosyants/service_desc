from typing import Any
from sqlalchemy.orm import DeclarativeBase

Base = DeclarativeBase


def map_db_model_to_dict(obj: Base) -> dict[str, Any]:
    """
    Преобразует объект модели SQLAlchemy в словарь.
    """
    obj_dict = {
        key: value for key, value in obj.__dict__.items() if not key.startswith("_")
    }
    for key, value in obj_dict.items():
        if isinstance(value, Base):
            obj_dict[key] = map_db_model_to_dict(value)
        if isinstance(value, list):
            obj_dict[key] = [
                map_db_model_to_dict(item) if isinstance(item, Base) else item
                for item in value
            ]

    return obj_dict
