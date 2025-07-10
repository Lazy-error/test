from pydantic import BaseModel
from ..models import Role


class InviteCreate(BaseModel):
    role: Role | None = None


class InviteUseTelegram(BaseModel):
    invite_token: str
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    auth_date: int
    hash: str


class InviteUseBot(BaseModel):
    invite_token: str
    telegram_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    bot_token: str
