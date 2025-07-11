from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..schemas.athlete import AthleteCreate, Athlete as AthleteSchema
from ..services.db import get_session
from ..models import Athlete, Workout
from .auth import get_current_user, require_roles, Role

router = APIRouter(prefix="/athletes", tags=["athletes"])

@router.get("/", response_model=List[AthleteSchema])
async def list_athletes(include_inactive: bool = False, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        query = session.query(Athlete)
        if not include_inactive:
            query = query.filter(Athlete.is_active.is_(True))
        return query.all()

@router.post("/", response_model=AthleteSchema)
async def create_athlete(athlete: AthleteCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = Athlete(**athlete.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

@router.get("/{athlete_id}", response_model=AthleteSchema)
async def get_athlete(athlete_id: int, user=Depends(get_current_user)):
    with get_session() as session:
        obj = session.get(Athlete, athlete_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj

@router.patch("/{athlete_id}", response_model=AthleteSchema)
async def update_athlete(athlete_id: int, athlete: AthleteCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Athlete, athlete_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        for key, value in athlete.model_dump().items():
            setattr(obj, key, value)
        session.commit()
        session.refresh(obj)
        return obj

@router.delete("/{athlete_id}")
async def delete_athlete(athlete_id: int, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Athlete, athlete_id)
        if obj:
            session.delete(obj)
            session.commit()
    return {"status": "deleted"}

@router.get("/{athlete_id}/workouts", response_model=List[dict])
async def athlete_workouts(athlete_id: int, user=Depends(get_current_user)):
    with get_session() as session:
        return session.query(Workout).filter(Workout.athlete_id == athlete_id).all()


@router.post("/{athlete_id}/deactivate", response_model=AthleteSchema)
async def deactivate_athlete(athlete_id: int, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Athlete, athlete_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        obj.is_active = False
        session.commit()
        session.refresh(obj)
        return obj


@router.post("/{athlete_id}/activate", response_model=AthleteSchema)
async def activate_athlete(athlete_id: int, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    with get_session() as session:
        obj = session.get(Athlete, athlete_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        obj.is_active = True
        session.commit()
        session.refresh(obj)
        return obj
