from pydantic import BaseModel

class AthleteBase(BaseModel):
    name: str

class AthleteCreate(AthleteBase):
    pass

class Athlete(AthleteBase):
    id: int

    class Config:
        orm_mode = True
