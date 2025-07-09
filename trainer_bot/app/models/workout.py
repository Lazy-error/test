from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    notes = Column(String)

    athlete = relationship("Athlete", backref="workouts")
    sets = relationship("Set", back_populates="workout", cascade="all, delete-orphan")
