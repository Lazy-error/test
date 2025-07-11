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
        # Ensure the connection can be established when the application starts
        with engine.connect():
            pass
        return engine
    except Exception as exc:
        raise RuntimeError(
            f"Unable to connect to the database at {db_url}. Ensure PostgreSQL is running and the DATABASE_URL is correct."
        ) from exc

engine = _create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import models so that metadata is populated before creating tables
from .. import models  # noqa: F401,E402

_initialized = False


def _init_db():
    global _initialized
    if _initialized:
        return
    Base.metadata.create_all(bind=engine)
    _initialized = True

def get_engine():
    return engine

def get_session():
    _init_db()
    return SessionLocal()
