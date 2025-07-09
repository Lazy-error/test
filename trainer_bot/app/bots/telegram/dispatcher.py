from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from datetime import date
from ...services.db import get_session
from ...models import Workout, Set
import httpx
import os

API_TOKEN = os.getenv("BOT_TOKEN", "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")

bot = Bot(API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello! This is Trainer Bot")

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer("Available commands: /start /help /today /future /proxy")

@dp.message(Command("today"))
async def today_cmd(message: Message):
    today = date.today().isoformat()
    with get_session() as session:
        todays = session.query(Workout).filter(Workout.date == today).all()
    if todays:
        for w in todays:
            await message.answer(f"{w.title}")
            sets = session.query(Set).filter(Set.workout_id == w.id).all()
            for s in sets:
                kb = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="20kg×5", callback_data=f"set:{s.id}:20:5"),
                    InlineKeyboardButton(text="25kg×5", callback_data=f"set:{s.id}:25:5")
                ]])
                await message.answer(f"{s.exercise} {s.weight}×{s.reps}", reply_markup=kb)
    else:
        await message.answer("No workouts for today.")

@dp.message(Command("proxy"))
async def proxy_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /proxy <text>")
        return
    text = parts[1]
    trainer_chat = os.getenv("TRAINER_CHAT_ID")
    athlete_chat = os.getenv("ATHLETE_CHAT_ID")
    dest = athlete_chat if str(message.chat.id) == trainer_chat else trainer_chat
    if dest:
        await bot.send_message(dest, text)

@dp.message(Command("future"))
async def future_cmd(message: Message):
    today = date.today()
    with get_session() as session:
        items = session.query(Workout).filter(Workout.date >= today).all()
    if not items:
        await message.answer("No future workouts")
        return
    text = "Upcoming workouts:\n" + "\n".join(f"{w.date} {w.title}" for w in items)
    await message.answer(text)

@dp.callback_query(lambda c: c.data.startswith("set:"))
async def set_callback(call: CallbackQuery):
    _, set_id, weight, reps = call.data.split(":")
    set_id = int(set_id)
    async with httpx.AsyncClient() as client:
        with get_session() as session:
            obj = session.get(Set, set_id)
        if not obj:
            await call.answer("Set not found")
            return
        payload = {
            "workout_id": obj.workout_id,
            "exercise": obj.exercise,
            "weight": float(weight),
            "reps": int(reps),
            "order": obj.order,
        }
        url = f"http://localhost:8000/api/v1/sets/{set_id}"
        await client.patch(url, json=payload)
    await call.answer("Updated")

