import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default to a local PostgreSQL database. This can be overridden with the
# `DATABASE_URL` environment variable.
DEFAULT_POSTGRES_URL = "postgresql://trainer:trainer@localhost:5432/trainer"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_POSTGRES_URL)

def _create_engine(db_url: str):
    try:
        engine = create_engine(db_url)
        # Attempt to connect to ensure required driver and server are available
        with engine.connect():
            pass
        return engine
    except Exception:
        return None

engine = _create_engine(DATABASE_URL)
if engine is None:
    # Fall back to SQLite for development and testing
    DATABASE_URL = "sqlite:///./trainer_bot.db"
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import models so that metadata is populated before creating tables
from .. import models  # noqa: F401,E402

Base.metadata.create_all(bind=engine)

def get_engine():
    return engine

def get_session():
    return SessionLocal()
