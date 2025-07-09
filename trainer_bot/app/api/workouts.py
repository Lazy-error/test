from fastapi import APIRouter
from typing import List

from ..schemas.workout import WorkoutCreate, Workout
from ..services.db import workouts_db

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.get("/", response_model=List[Workout])
async def list_workouts():
    return list(workouts_db.values())

@router.post("/", response_model=Workout)
async def create_workout(workout: WorkoutCreate):
    new_id = max(workouts_db.keys(), default=0) + 1
    data = workout.dict()
    data["id"] = new_id
    workouts_db[new_id] = data
    return data
