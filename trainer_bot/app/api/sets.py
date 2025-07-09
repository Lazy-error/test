from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..schemas.set import SetCreate, Set
from ..services.db import SessionLocal
from ..models import Set as SetModel

router = APIRouter(prefix="/sets", tags=["sets"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Set)
def create_set(set_in: SetCreate, db: Session = Depends(get_db)):
    db_set = SetModel(**set_in.dict())
    db.add(db_set)
    db.commit()
    db.refresh(db_set)
    return db_set

@router.get("/", response_model=List[Set])
def list_sets(db: Session = Depends(get_db)):
    return db.query(SetModel).all()
