from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas.athlete import AthleteCreate, Athlete
from ..services.db import athletes_db, workouts_db

router = APIRouter(prefix="/athletes", tags=["athletes"])

@router.get("/", response_model=List[Athlete])
async def list_athletes():
    return list(athletes_db.values())

@router.post("/", response_model=Athlete)
async def create_athlete(athlete: AthleteCreate):
    new_id = max(athletes_db.keys(), default=0) + 1
    data = athlete.model_dump()
    data["id"] = new_id
    athletes_db[new_id] = data
    return data

@router.get("/{athlete_id}", response_model=Athlete)
async def get_athlete(athlete_id: int):
    if athlete_id not in athletes_db:
        raise HTTPException(status_code=404, detail="Not found")
    return athletes_db[athlete_id]

@router.patch("/{athlete_id}", response_model=Athlete)
async def update_athlete(athlete_id: int, athlete: AthleteCreate):
    if athlete_id not in athletes_db:
        raise HTTPException(status_code=404, detail="Not found")
    data = athlete.model_dump()
    data["id"] = athlete_id
    athletes_db[athlete_id] = data
    return data

@router.delete("/{athlete_id}")
async def delete_athlete(athlete_id: int):
    if athlete_id in athletes_db:
        del athletes_db[athlete_id]
    return {"status": "deleted"}

@router.get("/{athlete_id}/workouts", response_model=List[dict])
async def athlete_workouts(athlete_id: int):
    return [w for w in workouts_db.values() if w.get("athlete_id") == athlete_id]
