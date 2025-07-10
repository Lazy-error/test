from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
import json
from datetime import date
from ...services.db import get_session
from ...models import Workout, Set
import httpx
import os
from typing import Dict, Any

API_TOKEN = os.getenv("BOT_TOKEN", "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")

bot = Bot(API_TOKEN)
dp = Dispatcher()

# simple in-memory state storage for interactive flows
user_states: Dict[int, Dict[str, Any]] = {}


async def show_menu(chat_id: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Today's workouts", callback_data="cmd:today")],
            [InlineKeyboardButton(text="Upcoming workouts", callback_data="cmd:future")],
            [InlineKeyboardButton(text="Add athlete", callback_data="cmd:add_athlete")],
            [InlineKeyboardButton(text="Add workout", callback_data="cmd:add_workout")],
            [InlineKeyboardButton(text="Send message", callback_data="cmd:proxy")],
            [InlineKeyboardButton(text="Help", callback_data="cmd:help")],
        ]
    )
    await bot.send_message(chat_id, "Choose an action:", reply_markup=kb)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello! This is Trainer Bot")
    await show_menu(message.chat.id)


@dp.message(Command("menu"))
async def menu_cmd(message: Message):
    await show_menu(message.chat.id)

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "Available commands: /start /menu /help /today /future /proxy /api /add_athlete /add_workout"
    )

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


@dp.message(Command("api"))
async def api_cmd(message: Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        await message.answer("Usage: /api <method> <path> [json]")
        return
    method = parts[1].upper()
    path = parts[2]
    data = None
    if len(parts) == 4:
        try:
            data = json.loads(parts[3])
        except json.JSONDecodeError:
            await message.answer("Invalid JSON payload")
            return
    token = os.getenv("TRAINER_API_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        resp = await client.request(method, path, json=data, headers=headers)
    text = resp.text
    if len(text) > 4000:
        text = text[:3990] + "..."
    await message.answer(f"Status {resp.status_code}\n{text}")


@dp.callback_query(lambda c: c.data.startswith("cmd:"))
async def menu_callback(call: CallbackQuery):
    action = call.data.split(":", 1)[1]
    if action == "today":
        await today_cmd(call.message)
    elif action == "future":
        await future_cmd(call.message)
    elif action == "help":
        await help_cmd(call.message)
    elif action == "proxy":
        await call.message.answer("Send message using /proxy <text>")
    elif action == "add_athlete":
        await add_athlete_cmd(call.message)
    elif action == "add_workout":
        await add_workout_cmd(call.message)
    await call.answer()

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


@dp.message(Command("add_athlete"))
async def add_athlete_cmd(message: Message):
    user_states[message.chat.id] = {"cmd": "add_athlete", "step": "name"}
    await message.answer("Enter athlete name:")


@dp.message(Command("add_workout"))
async def add_workout_cmd(message: Message):
    user_states[message.chat.id] = {"cmd": "add_workout", "step": "athlete"}
    await message.answer("Enter athlete id:")


@dp.message()
async def handle_flow(message: Message):
    state = user_states.get(message.chat.id)
    if not state:
        return
    token = os.getenv("TRAINER_API_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if state["cmd"] == "add_athlete" and state["step"] == "name":
        name = message.text.strip()
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            resp = await client.post("/api/v1/athletes/", json={"name": name}, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            await message.answer(f"Athlete created with id {data.get('id')}")
        else:
            await message.answer(f"Failed to create athlete: {resp.text}")
        user_states.pop(message.chat.id, None)
    elif state["cmd"] == "add_workout":
        if state["step"] == "athlete":
            state["athlete_id"] = message.text.strip()
            state["step"] = "date"
            await message.answer("Enter date (YYYY-MM-DD):")
        elif state["step"] == "date":
            state["date"] = message.text.strip()
            state["step"] = "type"
            await message.answer("Enter type:")
        elif state["step"] == "type":
            state["type"] = message.text.strip()
            state["step"] = "title"
            await message.answer("Enter title:")
        elif state["step"] == "title":
            state["title"] = message.text.strip()
            payload = {
                "athlete_id": int(state["athlete_id"]),
                "date": state["date"],
                "type": state["type"],
                "title": state["title"],
            }
            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                resp = await client.post("/api/v1/workouts/", json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                await message.answer(f"Workout created with id {data.get('id')}")
            else:
                await message.answer(f"Failed to create workout: {resp.text}")
            user_states.pop(message.chat.id, None)

