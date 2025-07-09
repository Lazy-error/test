from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas.workout import WorkoutCreate, Workout
from ..services.db import workouts_db, sets_db

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.get("/", response_model=List[Workout])
async def list_workouts():
    return list(workouts_db.values())

@router.post("/", response_model=Workout)
async def create_workout(workout: WorkoutCreate):
    new_id = max(workouts_db.keys(), default=0) + 1
    data = workout.model_dump()
    data["id"] = new_id
    workouts_db[new_id] = data
    return data

@router.get("/{workout_id}", response_model=Workout)
async def get_workout(workout_id: int):
    if workout_id not in workouts_db:
        raise HTTPException(status_code=404, detail="Not found")
    return workouts_db[workout_id]

@router.patch("/{workout_id}", response_model=Workout)
async def update_workout(workout_id: int, workout: WorkoutCreate):
    if workout_id not in workouts_db:
        raise HTTPException(status_code=404, detail="Not found")
    data = workout.model_dump()
    data["id"] = workout_id
    workouts_db[workout_id] = data
    return data

@router.delete("/{workout_id}")
async def delete_workout(workout_id: int):
    if workout_id in workouts_db:
        del workouts_db[workout_id]
    return {"status": "deleted"}

@router.get("/{workout_id}/sets", response_model=List[dict])
async def workout_sets(workout_id: int):
    return [s for s in sets_db.values() if s.get("workout_id") == workout_id]

@router.post("/{workout_id}/sets", response_model=dict)
async def create_workout_set(workout_id: int, set_in: dict):
    new_id = max(sets_db.keys(), default=0) + 1
    data = set_in
    data["id"] = new_id
    data["workout_id"] = workout_id
    sets_db[new_id] = data
    return data
