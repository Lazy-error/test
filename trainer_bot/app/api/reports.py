from fastapi import APIRouter
from typing import List
from ..services.db import get_session
from ..models import Workout

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/daily")
async def daily_report(date: str):
    with get_session() as session:
        items = session.query(Workout).filter(Workout.date == date).all()
        return {"date": date, "workouts": [w.__dict__ for w in items]}
