from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..schemas.athlete import AthleteCreate, Athlete
from ..services.db import SessionLocal
from ..models import Athlete as AthleteModel

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/athletes", tags=["athletes"])

@router.get("/", response_model=List[Athlete])
def list_athletes(db: Session = Depends(get_db)):
    return db.query(AthleteModel).all()

@router.post("/", response_model=Athlete)
def create_athlete(athlete: AthleteCreate, db: Session = Depends(get_db)):
    db_athlete = AthleteModel(name=athlete.name)
    db.add(db_athlete)
    db.commit()
    db.refresh(db_athlete)
    return db_athlete
