from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..schemas.workout import WorkoutCreate, Workout as WorkoutSchema
from ..services.db import get_session
from ..models import Workout, Set
from ..schemas.set import SetCreate
from .auth import get_current_user, require_roles, Role

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.get("/", response_model=List[WorkoutSchema])
async def list_workouts(user=Depends(get_current_user)):
    with get_session() as session:
        return session.query(Workout).all()

@router.post("/", response_model=WorkoutSchema)
async def create_workout(workout: WorkoutCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = Workout(**workout.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

@router.get("/{workout_id}", response_model=WorkoutSchema)
async def get_workout(workout_id: int, user=Depends(get_current_user)):
    with get_session() as session:
        obj = session.get(Workout, workout_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj

@router.patch("/{workout_id}", response_model=WorkoutSchema)
async def update_workout(workout_id: int, workout: WorkoutCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Workout, workout_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        for key, value in workout.model_dump().items():
            setattr(obj, key, value)
        session.commit()
        session.refresh(obj)
        return obj

@router.delete("/{workout_id}")
async def delete_workout(workout_id: int, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Workout, workout_id)
        if obj:
            session.delete(obj)
            session.commit()
    return {"status": "deleted"}

@router.get("/{workout_id}/sets", response_model=List[dict])
async def workout_sets(workout_id: int, user=Depends(get_current_user)):
    with get_session() as session:
        return session.query(Set).filter(Set.workout_id == workout_id).all()

@router.post("/{workout_id}/sets", response_model=dict)
async def create_workout_set(workout_id: int, set_in: SetCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        data = set_in.model_dump()
        if data.get("weight") is None and data.get("distance_km") is None:
            raise HTTPException(status_code=400, detail="Missing metrics")
        obj = Set(workout_id=workout_id, **data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj.__dict__
