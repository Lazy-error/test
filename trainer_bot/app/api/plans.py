from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.plan import PlanCreate, Plan
from ..services.db import plans_db

router = APIRouter(prefix="/plans", tags=["plans"])

@router.get("/", response_model=List[Plan])
async def list_plans():
    return list(plans_db.values())

@router.post("/", response_model=Plan)
async def create_plan(plan: PlanCreate):
    new_id = max(plans_db.keys(), default=0) + 1
    data = plan.model_dump()
    data["id"] = new_id
    plans_db[new_id] = data
    return data

@router.get("/{plan_id}", response_model=Plan)
async def get_plan(plan_id: int):
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail="Not found")
    return plans_db[plan_id]

@router.patch("/{plan_id}", response_model=Plan)
async def update_plan(plan_id: int, plan: PlanCreate):
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail="Not found")
    data = plan.model_dump()
    data["id"] = plan_id
    plans_db[plan_id] = data
    return data

@router.delete("/{plan_id}")
async def delete_plan(plan_id: int):
    if plan_id in plans_db:
        del plans_db[plan_id]
    return {"status": "deleted"}
