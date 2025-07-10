from pydantic import BaseModel
from ..models import Role

class TelegramAuth(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    auth_date: int
    hash: str
    role: Role | None = None

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str


class BotAuth(BaseModel):
    telegram_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    bot_token: str
    role: Role | None = None

class RoleUpdate(BaseModel):
    role: Role
