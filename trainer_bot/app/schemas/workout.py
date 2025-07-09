from pydantic import BaseModel
from datetime import date

class WorkoutBase(BaseModel):
    athlete_id: int
    date: date
    type: str
    title: str
    notes: str | None = None

class WorkoutCreate(WorkoutBase):
    pass

class Workout(WorkoutBase):
    id: int

    class Config:
        orm_mode = True
