import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def create_db_engine():
    db_url = settings.database_url_effective
    
    # If SQLite explicitly configured or dev fallback
    if "sqlite" in db_url:
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=settings.debug and settings.env == "development",
        )
    
    # Try PostgreSQL, fallback to local SQLite if PostgreSQL is not running
    try:
        eng = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 2} if "psycopg" in db_url else {},
            echo=settings.debug and settings.env == "development",
        )
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return eng
    except Exception as e:
        # Log prominently — silent fallback masks real connectivity problems
        logging.getLogger(__name__).critical(
            "PostgreSQL unavailable (%s). Falling back to SQLite at %s — "
            "JSONB/UUID/Geography columns WILL break on writes!",
            e,
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'krishilink.db'),
        )
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sqlite_path = os.path.join(base_dir, "krishilink.db")
        sqlite_url = f"sqlite:///{sqlite_path}"
        return create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
        )


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

