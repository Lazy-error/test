from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas.set import SetCreate, Set
from ..services.db import sets_db

router = APIRouter(prefix="/sets", tags=["sets"])

@router.get("/", response_model=List[Set])
async def list_sets():
    return list(sets_db.values())

@router.post("/", response_model=Set)
async def create_set(set_in: SetCreate):
    new_id = max(sets_db.keys(), default=0) + 1
    data = set_in.model_dump()
    data["id"] = new_id
    sets_db[new_id] = data
    return data

@router.patch("/{set_id}", response_model=Set)
async def update_set(set_id: int, set_in: SetCreate):
    if set_id not in sets_db:
        raise HTTPException(status_code=404, detail="Not found")
    data = set_in.model_dump()
    data["id"] = set_id
    sets_db[set_id] = data
    return data
