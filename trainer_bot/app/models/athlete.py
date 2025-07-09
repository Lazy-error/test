from sqlalchemy import Column, Integer, String

from .base import Base

class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
