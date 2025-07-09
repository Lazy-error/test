from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from .base import Base

class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise = Column(String, nullable=False)
    weight = Column(Float)
    reps = Column(Integer)
    order = Column(Integer)

    workout = relationship("Workout", back_populates="sets")
