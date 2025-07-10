import hashlib
import hmac
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..schemas.auth import TelegramAuth, TokenPair, RefreshRequest, BotAuth
from ..services.db import get_session
from ..models import User
import jwt
import datetime

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_EXPIRE_MIN = 15
REFRESH_EXPIRE_DAYS = 30

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


def create_access_token(user_id: int) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + datetime.timedelta(minutes=ACCESS_EXPIRE_MIN),
        "jti": os.urandom(8).hex(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + datetime.timedelta(days=REFRESH_EXPIRE_DAYS),
        "jti": os.urandom(8).hex(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def verify_telegram(data: dict) -> bool:
    token = os.getenv("BOT_TOKEN", "")
    secret = hashlib.sha256(token.encode()).digest()
    check_hash = data.pop("hash", "")
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    hmac_hash = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    return hmac_hash == check_hash


@router.post("/telegram", response_model=TokenPair)
async def telegram_auth(auth: TelegramAuth):
    data = auth.model_dump(exclude_none=True)
    if not verify_telegram(data.copy()):
        raise HTTPException(status_code=400, detail="invalid auth data")
    with get_session() as session:
        user = session.query(User).filter(User.telegram_id == auth.id).first()
        if not user:
            user = User(
                telegram_id=auth.id,
                first_name=auth.first_name,
                last_name=auth.last_name,
                username=auth.username,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        user.refresh_token = refresh
        session.commit()
        return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/bot", response_model=TokenPair)
async def bot_auth(data: BotAuth):
    bot_token = os.getenv("BOT_TOKEN", "")
    if data.bot_token != bot_token:
        raise HTTPException(status_code=401, detail="invalid bot token")
    with get_session() as session:
        user = session.query(User).filter(User.telegram_id == data.telegram_id).first()
        if not user:
            user = User(
                telegram_id=data.telegram_id,
                first_name=data.first_name,
                last_name=data.last_name,
                username=data.username,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        user.refresh_token = refresh
        session.commit()
        return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(data: RefreshRequest):
    try:
        payload = decode_token(data.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="invalid token type")
    user_id = payload.get("sub")
    with get_session() as session:
        user = session.get(User, user_id)
        if not user or user.refresh_token != data.refresh_token:
            raise HTTPException(status_code=401, detail="invalid token")
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        user.refresh_token = refresh
        session.commit()
        return TokenPair(access_token=access, refresh_token=refresh)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token type")
    user_id = payload.get("sub")
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")
        return user


def require_roles(roles: list[str]):
    def dependency(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return user

    return dependency
