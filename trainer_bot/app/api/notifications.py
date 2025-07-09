from fastapi import APIRouter
from typing import List
from ..schemas.notification import Notification
from ..services.db import notifications_db

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[Notification])
async def list_notifications():
    return list(notifications_db.values())
