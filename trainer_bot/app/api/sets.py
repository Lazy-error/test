from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..schemas.set import SetCreate, Set as SetSchema
from ..services.db import get_session
from ..models import Set
from .auth import get_current_user

router = APIRouter(prefix="/sets", tags=["sets"])

@router.get("/", response_model=List[SetSchema])
async def list_sets(user=Depends(get_current_user)):
    with get_session() as session:
        return session.query(Set).all()

@router.post("/", response_model=SetSchema)
async def create_set(set_in: SetCreate, user=Depends(get_current_user)):
    with get_session() as session:
        obj = Set(**set_in.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

@router.patch("/{set_id}", response_model=SetSchema)
async def update_set(set_id: int, set_in: SetCreate, user=Depends(get_current_user)):
    with get_session() as session:
        obj = session.get(Set, set_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        for key, value in set_in.model_dump().items():
            setattr(obj, key, value)
        session.commit()
        session.refresh(obj)
        return obj
