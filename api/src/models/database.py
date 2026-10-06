import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# connect_args is required for SQLite to allow multi-threaded access.
# Ignored by PostgreSQL when DATABASE_URL is switched.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    """Create all tables. Called once on application startup."""
    from src.models import schemas  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency: yield a database session and close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
