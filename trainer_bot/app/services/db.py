import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trainer_bot.db")

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
