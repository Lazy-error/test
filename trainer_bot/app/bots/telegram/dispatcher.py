from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
import os
from datetime import date

from ..services.db import SessionLocal
from ..models import Athlete, Workout

API_TOKEN = os.getenv("BOT_TOKEN", "test-token")

bot = Bot(API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello! This is Trainer Bot")

@dp.message(Command("today"))
async def today(message: Message):
    db = SessionLocal()
    athlete = db.query(Athlete).filter_by(id=message.from_user.id).first()
    if not athlete:
        athlete = Athlete(id=message.from_user.id, name=message.from_user.full_name)
        db.add(athlete)
        db.commit()
    workouts = db.query(Workout).filter_by(athlete_id=athlete.id, date=date.today()).all()
    if not workouts:
        await message.answer("No workouts today")
    else:
        titles = "\n".join(w.title for w in workouts)
        await message.answer(f"Today's workouts:\n{titles}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
