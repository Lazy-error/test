from sqlalchemy import Column, Integer, String, Date, Time, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime

from enum import Enum

from .services.db import Base

class Role(str, Enum):
    coach = "coach"
    athlete = "athlete"
    superadmin = "superadmin"


class MetricType(str, Enum):
    strength = "strength"
    cardio = "cardio"


class Exercise(Base):
    __tablename__ = 'exercises'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    metric_type = Column(String, nullable=False)

class Athlete(Base):
    __tablename__ = 'athletes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contraindications = Column(String(250))
    is_active = Column(Boolean, default=True, nullable=False)

    workouts = relationship('Workout', back_populates='athlete')

class Workout(Base):
    __tablename__ = 'workouts'
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    notes = Column(Text)

    athlete = relationship('Athlete', back_populates='workouts')
    sets = relationship('Set', back_populates='workout')

class Set(Base):
    __tablename__ = 'sets'
    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey('workouts.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.id'), nullable=False)
    weight = Column(Float, nullable=True)
    reps = Column(Integer, nullable=True)
    distance_km = Column(Float, nullable=True)
    duration_sec = Column(Integer, nullable=True)
    avg_hr = Column(Integer, nullable=True)
    status = Column(String, default="confirmed", nullable=False)
    order = Column(Integer, nullable=False)

    workout = relationship('Workout', back_populates='sets')
    exercise = relationship('Exercise')

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
    role = Column(String, default=Role.athlete.value, nullable=False)
    refresh_token = Column(String, nullable=True)
    timezone = Column(String, default="Europe/Moscow")


class Invite(Base):
    __tablename__ = 'invites'
    id = Column(Integer, primary_key=True)
    jti = Column(String, unique=True, nullable=False)
    role = Column(String, default=Role.athlete.value, nullable=False)
    issued_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    issued_at = Column(DateTime, default=datetime.datetime.utcnow)
