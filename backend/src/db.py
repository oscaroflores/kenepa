from collections.abc import Generator
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import get_settings
from src.models import Base

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

_schema_initialized = False


def initialize_runtime_schema() -> None:
    global _schema_initialized
    if _schema_initialized or not (os.getenv("VERCEL") or os.getenv("AUTO_CREATE_SCHEMA") == "1"):
        return
    Base.metadata.create_all(bind=engine)
    _schema_initialized = True


def get_session() -> Generator[Session, None, None]:
    initialize_runtime_schema()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
