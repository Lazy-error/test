from pydantic import BaseModel

class User(BaseModel):
    id: int
    role: str
    timezone: str | None = None

    class Config:
        from_attributes = True
