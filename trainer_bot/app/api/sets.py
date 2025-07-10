from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..schemas.set import SetCreate, SetUpdate, Set as SetSchema
from ..services.db import get_session
from ..models import Set
from .auth import get_current_user, require_roles, Role

router = APIRouter(prefix="/sets", tags=["sets"])

@router.get("/", response_model=List[SetSchema])
async def list_sets(user=Depends(get_current_user)):
    with get_session() as session:
        return session.query(Set).all()

@router.post("/", response_model=SetSchema)
async def create_set(set_in: SetCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        data = set_in.model_dump()
        if data.get("weight") is None and data.get("distance_km") is None:
            raise HTTPException(status_code=400, detail="Missing metrics")
        obj = Set(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

@router.patch("/{set_id}", response_model=SetSchema)
async def update_set(set_id: int, set_in: SetUpdate, user=Depends(require_roles([Role.coach, Role.superadmin, Role.athlete]))):
    with get_session() as session:
        obj = session.get(Set, set_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        for key, value in set_in.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        if user.role == Role.athlete:
            obj.status = "pending"
        session.commit()
        session.refresh(obj)
        return obj


@router.post("/{set_id}/status", response_model=SetSchema)
async def review_set(set_id: int, status: str, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    if status not in {"confirmed", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status")
    with get_session() as session:
        obj = session.get(Set, set_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        obj.status = status
        session.commit()
        session.refresh(obj)
        return obj
