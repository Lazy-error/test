from fastapi import APIRouter, Depends
from .auth import require_roles

router = APIRouter(prefix="/protected", tags=["protected"])

@router.get("/ping")
async def protected_ping(user=Depends(require_roles(["user"]))):
    return {"status": "ok", "user_id": user.id}
