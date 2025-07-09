from pydantic import BaseModel

class SetBase(BaseModel):
    workout_id: int
    exercise: str
    weight: float | None = None
    reps: int | None = None
    order: int | None = None

class SetCreate(SetBase):
    pass

class Set(SetBase):
    id: int

    class Config:
        orm_mode = True
