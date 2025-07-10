from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..schemas.plan import PlanCreate, Plan as PlanSchema
from ..services.db import get_session
from ..models import Plan
from .auth import get_current_user, require_roles, Role

router = APIRouter(prefix="/plans", tags=["plans"])

@router.get("/", response_model=List[PlanSchema])
async def list_plans(user=Depends(get_current_user)):
    with get_session() as session:
        return session.query(Plan).all()

@router.post("/", response_model=PlanSchema)
async def create_plan(plan: PlanCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = Plan(**plan.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

@router.get("/{plan_id}", response_model=PlanSchema)
async def get_plan(plan_id: int, user=Depends(get_current_user)):
    with get_session() as session:
        obj = session.get(Plan, plan_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj

@router.patch("/{plan_id}", response_model=PlanSchema)
async def update_plan(plan_id: int, plan: PlanCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Plan, plan_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        for key, value in plan.model_dump().items():
            setattr(obj, key, value)
        session.commit()
        session.refresh(obj)
        return obj

@router.delete("/{plan_id}")
async def delete_plan(plan_id: int, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Plan, plan_id)
        if obj:
            session.delete(obj)
            session.commit()
    return {"status": "deleted"}
