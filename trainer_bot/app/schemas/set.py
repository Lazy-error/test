from pydantic import BaseModel

class SetBase(BaseModel):
    workout_id: int
    exercise: str
    weight: float
    reps: int
    order: int

class SetCreate(SetBase):
    pass

class Set(SetBase):
    id: int

    class Config:
        from_attributes = True
