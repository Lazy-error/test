from fastapi import APIRouter, Depends
from typing import List
from ..schemas.notification import Notification as NotificationSchema
from ..services.db import get_session
from ..models import Notification
from .auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[NotificationSchema])
async def list_notifications(user=Depends(get_current_user)):
    with get_session() as session:
        return session.query(Notification).all()
