from fastapi import APIRouter, Request
from aiogram.types import Update
from ..bots.telegram.dispatcher import dp, bot

router = APIRouter(tags=["telegram"])

@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}
