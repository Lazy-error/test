from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..schemas.workout import WorkoutCreate, Workout
from ..services.db import SessionLocal
from ..models import Workout as WorkoutModel

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.get("/", response_model=List[Workout])
def list_workouts(db: Session = Depends(get_db)):
    return db.query(WorkoutModel).all()

@router.post("/", response_model=Workout)
def create_workout(workout: WorkoutCreate, db: Session = Depends(get_db)):
    db_workout = WorkoutModel(**workout.dict())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout
