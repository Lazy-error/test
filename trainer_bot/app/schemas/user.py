from pydantic import BaseModel

class User(BaseModel):
    id: int
    role: str

    class Config:
        from_attributes = True
