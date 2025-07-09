from pydantic import BaseModel

class PlanBase(BaseModel):
    title: str
    notes: str | None = None

class PlanCreate(PlanBase):
    pass

class Plan(PlanBase):
    id: int

    class Config:
        from_attributes = True
