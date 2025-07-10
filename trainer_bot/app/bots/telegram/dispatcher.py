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
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

bot = Bot(API_TOKEN)
dp = Dispatcher()

# simple in-memory state storage for interactive flows
user_states: Dict[int, Dict[str, Any]] = {}


async def show_menu(chat_id: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Тренировки на сегодня", callback_data="cmd:today")],
            [InlineKeyboardButton(text="Предстоящие тренировки", callback_data="cmd:future")],
            [InlineKeyboardButton(text="Добавить атлета", callback_data="cmd:add_athlete")],
            [InlineKeyboardButton(text="Добавить тренировку", callback_data="cmd:add_workout")],
            [InlineKeyboardButton(text="Отправить сообщение", callback_data="cmd:proxy")],
            [InlineKeyboardButton(text="Помощь", callback_data="cmd:help")],
        ]
    )
    await bot.send_message(chat_id, "Выберите действие:", reply_markup=kb)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Это Trainer Bot")
    await show_menu(message.chat.id)


@dp.message(Command("menu"))
async def menu_cmd(message: Message):
    await show_menu(message.chat.id)

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "Доступные команды: /start /menu /help /today /future /proxy /api /add_athlete /add_workout"
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
        await message.answer("На сегодня тренировок нет.")

@dp.message(Command("proxy"))
async def proxy_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /proxy <текст>")
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
        await message.answer("Нет запланированных тренировок")
        return
    text = "Ближайшие тренировки:\n" + "\n".join(f"{w.date} {w.title}" for w in items)
    await message.answer(text)


@dp.message(Command("api"))
async def api_cmd(message: Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        await message.answer("Использование: /api <method> <path> [json]")
        return
    method = parts[1].upper()
    path = parts[2]
    data = None
    if len(parts) == 4:
        try:
            data = json.loads(parts[3])
        except json.JSONDecodeError:
            await message.answer("Некорректный JSON")
            return
    token = os.getenv("TRAINER_API_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.request(method, path, json=data, headers=headers)
        except httpx.RequestError:
            await message.answer("Не удалось подключиться к серверу")
            return
    text = resp.text
    if len(text) > 4000:
        text = text[:3990] + "..."
    await message.answer(f"Статус {resp.status_code}\n{text}")


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
        await call.message.answer("Отправьте сообщение с помощью /proxy <текст>")
    elif action == "add_athlete":
        await add_athlete_cmd(call.message)
    elif action == "add_workout":
        await add_workout_cmd(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("set:"))
async def set_callback(call: CallbackQuery):
    _, set_id, weight, reps = call.data.split(":")
    set_id = int(set_id)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        with get_session() as session:
            obj = session.get(Set, set_id)
        if not obj:
            await call.answer("Сет не найден")
            return
        payload = {
            "workout_id": obj.workout_id,
            "exercise": obj.exercise,
            "weight": float(weight),
            "reps": int(reps),
            "order": obj.order,
        }
        url = f"/api/v1/sets/{set_id}"
        try:
            await client.patch(url, json=payload)
        except httpx.RequestError:
            await call.answer("Ошибка соединения")
            return
    await call.answer("Обновлено")


@dp.message(Command("add_athlete"))
async def add_athlete_cmd(message: Message):
    user_states[message.chat.id] = {"cmd": "add_athlete", "step": "name"}
    await message.answer("Введите имя атлета (например, Иван Иванов):")


@dp.message(Command("add_workout"))
async def add_workout_cmd(message: Message):
    user_states[message.chat.id] = {"cmd": "add_workout", "step": "athlete"}
    await message.answer(
        "Создаём тренировку. Отправьте ID атлета (число):"
    )


@dp.message()
async def handle_flow(message: Message):
    state = user_states.get(message.chat.id)
    if not state:
        return
    token = os.getenv("TRAINER_API_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if state["cmd"] == "add_athlete" and state["step"] == "name":
        name = message.text.strip()
        async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
            try:
                resp = await client.post("/api/v1/athletes/", json={"name": name}, headers=headers)
            except httpx.RequestError:
                await message.answer("Не удалось подключиться к серверу")
                user_states.pop(message.chat.id, None)
                await show_menu(message.chat.id)
                return
            if resp.status_code == 200:
                data = resp.json()
                await message.answer(f"Атлет создан с id {data.get('id')}")
            else:
                await message.answer(f"Не удалось создать атлета: {resp.text}")
            user_states.pop(message.chat.id, None)
            await show_menu(message.chat.id)
    elif state["cmd"] == "add_workout":
        if state["step"] == "athlete":
            state["athlete_id"] = message.text.strip()
            state["step"] = "date"
            await message.answer("Введите дату тренировки (ГГГГ-ММ-ДД):")
        elif state["step"] == "date":
            state["date"] = message.text.strip()
            state["step"] = "type"
            await message.answer("Введите тип тренировки (например, силовая):")
        elif state["step"] == "type":
            state["type"] = message.text.strip()
            state["step"] = "title"
            await message.answer("Введите название тренировки:")
        elif state["step"] == "title":
            state["title"] = message.text.strip()
            payload = {
                "athlete_id": int(state["athlete_id"]),
                "date": state["date"],
                "type": state["type"],
                "title": state["title"],
            }
            async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
                try:
                    resp = await client.post("/api/v1/workouts/", json=payload, headers=headers)
                except httpx.RequestError:
                    await message.answer("Не удалось подключиться к серверу")
                    user_states.pop(message.chat.id, None)
                    await show_menu(message.chat.id)
                    return
            if resp.status_code == 200:
                data = resp.json()
                await message.answer(f"Тренировка создана с id {data.get('id')}")
            else:
                await message.answer(f"Не удалось создать тренировку: {resp.text}")
            user_states.pop(message.chat.id, None)
            await show_menu(message.chat.id)

