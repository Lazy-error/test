from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    text: str
    timestamp: datetime | None = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int

    class Config:
        from_attributes = True
