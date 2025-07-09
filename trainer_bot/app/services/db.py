import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trainer.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

from ..models import Base

def init_db():
    Base.metadata.create_all(bind=engine)
