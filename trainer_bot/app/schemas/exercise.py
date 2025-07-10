from pydantic import BaseModel
from ..models import MetricType

class ExerciseBase(BaseModel):
    name: str
    description: str | None = None
    metric_type: MetricType

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int

    class Config:
        orm_mode = True
