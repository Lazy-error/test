from sqlalchemy import Column, Integer, String, Date, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

from .services.db import Base

class Athlete(Base):
    __tablename__ = 'athletes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    workouts = relationship('Workout', back_populates='athlete')

class Workout(Base):
    __tablename__ = 'workouts'
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    notes = Column(Text)

    athlete = relationship('Athlete', back_populates='workouts')
    sets = relationship('Set', back_populates='workout')

class Set(Base):
    __tablename__ = 'sets'
    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey('workouts.id'), nullable=False)
    exercise = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    reps = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)

    workout = relationship('Workout', back_populates='sets')

class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    notes = Column(Text)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    role = Column(String, default='user', nullable=False)
    refresh_token = Column(String, nullable=True)
