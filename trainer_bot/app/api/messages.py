from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.message import MessageCreate, Message as MessageSchema
from ..services.db import get_session
from ..models import Message

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("/", response_model=List[MessageSchema])
async def list_messages():
    with get_session() as session:
        return session.query(Message).all()

@router.post("/", response_model=MessageSchema)
async def create_message(msg: MessageCreate):
    with get_session() as session:
        obj = Message(**msg.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
