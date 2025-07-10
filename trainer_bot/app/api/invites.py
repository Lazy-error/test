import os
import datetime
import jwt
from fastapi import APIRouter, Depends, HTTPException

from ..schemas.invite import InviteCreate, InviteUseTelegram, InviteUseBot
from ..schemas.auth import TokenPair
from ..services.db import get_session
from ..models import Invite, Role, User
from .auth import require_roles, verify_telegram, create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/invites", tags=["invites"])


def _create_invite_token(role: str, issuer_id: int) -> str:
    now = datetime.datetime.utcnow()
    jti = os.urandom(8).hex()
    payload = {
        "jti": jti,
        "type": "invite",
        "role": role,
        "iss": str(issuer_id),
        "iat": now,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    with get_session() as session:
        session.add(Invite(jti=jti, role=role, issued_by=issuer_id))
        session.commit()
    return token


@router.post("/", response_model=dict)
async def issue_invite(data: InviteCreate, user=Depends(require_roles([Role.coach, Role.superadmin]))):
    role = data.role.value if data.role else Role.athlete.value
    token = _create_invite_token(role, user.id)
    return {"invite_token": token}


@router.post("/telegram", response_model=TokenPair)
async def telegram_signup(auth: InviteUseTelegram):
    verify_data = auth.model_dump().copy()
    verify_data.pop("invite_token")
    if not verify_telegram(verify_data):
        raise HTTPException(status_code=400, detail="invalid auth data")
    try:
        payload = jwt.decode(auth.invite_token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=400, detail="invalid invite token")
    if payload.get("type") != "invite":
        raise HTTPException(status_code=400, detail="invalid invite token")
    jti = payload.get("jti")
    with get_session() as session:
        invite = session.query(Invite).filter(Invite.jti == jti, Invite.used.is_(False)).first()
        if not invite:
            raise HTTPException(status_code=400, detail="invite not found or used")
        user = session.query(User).filter(User.telegram_id == auth.id).first()
        if not user:
            user = User(
                telegram_id=auth.id,
                first_name=auth.first_name,
                last_name=auth.last_name,
                username=auth.username,
                role=invite.role,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        invite.used = True
        session.commit()
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        user.refresh_token = refresh
        session.commit()
        return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/bot", response_model=TokenPair)
async def bot_signup(data: InviteUseBot):
    bot_token = os.getenv("BOT_TOKEN", "")
    if data.bot_token != bot_token:
        raise HTTPException(status_code=401, detail="invalid bot token")
    try:
        payload = jwt.decode(data.invite_token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=400, detail="invalid invite token")
    if payload.get("type") != "invite":
        raise HTTPException(status_code=400, detail="invalid invite token")
    jti = payload.get("jti")
    with get_session() as session:
        invite = session.query(Invite).filter(Invite.jti == jti, Invite.used.is_(False)).first()
        if not invite:
            raise HTTPException(status_code=400, detail="invite not found or used")
        user = session.query(User).filter(User.telegram_id == data.telegram_id).first()
        if not user:
            user = User(
                telegram_id=data.telegram_id,
                first_name=data.first_name,
                last_name=data.last_name,
                username=data.username,
                role=invite.role,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        invite.used = True
        session.commit()
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        user.refresh_token = refresh
        session.commit()
        return TokenPair(access_token=access, refresh_token=refresh)
