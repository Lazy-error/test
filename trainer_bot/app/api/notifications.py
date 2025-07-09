from fastapi import APIRouter
from typing import List
from ..schemas.notification import Notification as NotificationSchema
from ..services.db import get_session
from ..models import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[NotificationSchema])
async def list_notifications():
    with get_session() as session:
        return session.query(Notification).all()
