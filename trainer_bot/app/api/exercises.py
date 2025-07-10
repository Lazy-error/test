from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..schemas.exercise import ExerciseCreate, Exercise as ExerciseSchema
from ..services.db import get_session
from ..models import Exercise, MetricType
from .auth import get_current_user, require_roles, Role

router = APIRouter(prefix="/exercises", tags=["exercises"])

@router.get("/", response_model=List[ExerciseSchema])
async def list_exercises(user=Depends(get_current_user)):
    with get_session() as session:
        return session.query(Exercise).all()

@router.post("/", response_model=ExerciseSchema)
async def create_exercise(ex: ExerciseCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = Exercise(**ex.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

@router.get("/{exercise_id}", response_model=ExerciseSchema)
async def get_exercise(exercise_id: int, user=Depends(get_current_user)):
    with get_session() as session:
        obj = session.get(Exercise, exercise_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj

@router.patch("/{exercise_id}", response_model=ExerciseSchema)
async def update_exercise(exercise_id: int, ex: ExerciseCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Exercise, exercise_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        for key, value in ex.model_dump().items():
            setattr(obj, key, value)
        session.commit()
        session.refresh(obj)
        return obj

@router.delete("/{exercise_id}")
async def delete_exercise(exercise_id: int, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Exercise, exercise_id)
        if obj:
            session.delete(obj)
            session.commit()
    return {"status": "deleted"}
