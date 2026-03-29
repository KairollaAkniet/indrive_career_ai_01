import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

# SQLite engine. check_same_thread=False нужен, чтобы SQLAlchemy работал корректно
# в окружениях разработки (FastAPI / uvicorn).
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Создаёт таблицы, если их ещё нет."""
    # Импорт Base гарантирует, что модели зарегистрированы в метаданных.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

