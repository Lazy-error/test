from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.message import MessageCreate, Message
from ..services.db import messages_db

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("/", response_model=List[Message])
async def list_messages():
    return list(messages_db.values())

@router.post("/", response_model=Message)
async def create_message(msg: MessageCreate):
    new_id = max(messages_db.keys(), default=0) + 1
    data = msg.model_dump()
    data["id"] = new_id
    messages_db[new_id] = data
    return data
