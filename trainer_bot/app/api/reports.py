from fastapi import APIRouter
from typing import List
from ..services.db import workouts_db

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/daily")
async def daily_report(date: str):
    items = [w for w in workouts_db.values() if str(w.get("date")) == date]
    return {"date": date, "workouts": items}
