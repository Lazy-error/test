from pydantic import BaseModel
from datetime import datetime

class Notification(BaseModel):
    id: int
    user_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True
