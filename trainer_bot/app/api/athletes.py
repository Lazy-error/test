from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas.athlete import AthleteCreate, Athlete
from ..services.db import DB, athletes_db

router = APIRouter(prefix="/athletes", tags=["athletes"])

@router.get("/", response_model=List[Athlete])
async def list_athletes():
    return list(athletes_db.values())

@router.post("/", response_model=Athlete)
async def create_athlete(athlete: AthleteCreate):
    new_id = max(athletes_db.keys(), default=0) + 1
    data = athlete.dict()
    data["id"] = new_id
    athletes_db[new_id] = data
    return data
