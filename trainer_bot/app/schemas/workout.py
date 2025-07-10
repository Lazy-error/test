from pydantic import BaseModel
from datetime import date, time as time_
from typing import Optional

class WorkoutBase(BaseModel):
    athlete_id: int
    date: date
    time: Optional[time_] = None
    type: str
    title: str
    notes: str | None = None

class WorkoutCreate(WorkoutBase):
    pass

class Workout(WorkoutBase):
    id: int

    class Config:
        orm_mode = True
