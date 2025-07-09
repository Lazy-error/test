from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from datetime import date
from ...services.db import workouts_db
import os

API_TOKEN = os.getenv("BOT_TOKEN", "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")

bot = Bot(API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello! This is Trainer Bot")

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer("Available commands: /start /help /today")

@dp.message(Command("today"))
async def today_cmd(message: Message):
    today = date.today().isoformat()
    todays = [w for w in workouts_db.values() if str(w.get("date")) == today]
    if todays:
        text = "Today's workouts:\n" + "\n".join(w["title"] for w in todays)
    else:
        text = "No workouts for today."
    await message.answer(text)
