from pydantic import BaseModel

class SetBase(BaseModel):
    workout_id: int
    exercise: str
    weight: float | None = None
    reps: int | None = None
    distance_km: float | None = None
    duration_sec: int | None = None
    avg_hr: int | None = None
    order: int
    status: str | None = "confirmed"

class SetCreate(SetBase):
    pass

class Set(SetBase):
    id: int

    class Config:
        from_attributes = True


class SetUpdate(BaseModel):
    weight: float | None = None
    reps: int | None = None
    distance_km: float | None = None
    duration_sec: int | None = None
    avg_hr: int | None = None
    order: int | None = None
    status: str | None = None
