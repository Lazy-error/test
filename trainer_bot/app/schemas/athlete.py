from pydantic import BaseModel

class AthleteBase(BaseModel):
    name: str
    contraindications: str | None = None

class AthleteCreate(AthleteBase):
    pass

class Athlete(AthleteBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
