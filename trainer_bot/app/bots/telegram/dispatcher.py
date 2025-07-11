from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
import json
from datetime import date
from ...services.db import get_session
from ...models import Workout, Set
from ...services.parser import parse_strength_cell
import httpx
import os
from typing import Dict, Any

API_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

bot = Bot(API_TOKEN)
dp = Dispatcher()

# simple in-memory state storage for interactive flows
user_states: Dict[int, Dict[str, Any]] = {}
user_tokens: Dict[int, str] = {}


async def get_auth_headers(tg_user) -> Dict[str, str]:
    token = os.getenv("TRAINER_API_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    cached = user_tokens.get(tg_user.id)
    if cached:
        return {"Authorization": f"Bearer {cached}"}
    payload = {
        "telegram_id": tg_user.id,
        "first_name": tg_user.first_name,
        "last_name": tg_user.last_name,
        "username": tg_user.username,
        "bot_token": API_TOKEN,
    }
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.post("/api/v1/auth/bot", json=payload)
        except httpx.RequestError:
            return {}
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        if token:
            user_tokens[tg_user.id] = token
            return {"Authorization": f"Bearer {token}"}
    return {}


async def _get_role(tg_user) -> str | None:
    headers = await get_auth_headers(tg_user)
    if not headers:
        return None
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get("/api/v1/auth/users/me", headers=headers)
        except httpx.RequestError:
            return None
    if resp.status_code == 200:
        return resp.json().get("role", "athlete")
    return "athlete"


async def _signup_with_invite(tg_user, token: str, message: Message) -> bool:
    payload = {
        "invite_token": token,
        "telegram_id": tg_user.id,
        "first_name": tg_user.first_name,
        "last_name": tg_user.last_name,
        "username": tg_user.username,
        "bot_token": API_TOKEN,
    }
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.post("/api/v1/invites/bot", json=payload)
        except httpx.RequestError:
            await message.answer("Не удалось подключиться к серверу")
            return False
    if resp.status_code == 200:
        access = resp.json().get("access_token")
        if access:
            user_tokens[tg_user.id] = access
        await message.answer("Регистрация успешна")
        return True
    if resp.status_code == 400:
        await message.answer("Инвайт просрочен или уже использован")
    else:
        await message.answer(f"Ошибка регистрации: {resp.text}")
    return False

async def show_menu(chat_id: int, tg_user=None):
    role = "athlete"
    if tg_user:
        role = await _get_role(tg_user)
    keyboard = [
        [InlineKeyboardButton(text="Тренировки на сегодня", callback_data="cmd:today")],
        [InlineKeyboardButton(text="Предстоящие тренировки", callback_data="cmd:future")],
    ]
    if role in ["coach", "superadmin"]:
        keyboard.extend([
            [InlineKeyboardButton(text="Добавить атлета", callback_data="cmd:add_athlete")],
            [InlineKeyboardButton(text="Добавить тренировку", callback_data="cmd:add_workout")],
            [InlineKeyboardButton(text="Добавить сет", callback_data="cmd:add_set")],
            [InlineKeyboardButton(text="Упражнения", callback_data="cmd:exercise")],
            [InlineKeyboardButton(text="Планы", callback_data="cmd:plans")],
            [InlineKeyboardButton(text="Инвайт", callback_data="cmd:invite")],
        ])
    keyboard.append([InlineKeyboardButton(text="Помощь", callback_data="cmd:help")])
    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.send_message(chat_id, "Выберите действие:", reply_markup=kb)

@dp.message(CommandStart())
async def start(message: Message):
    parts = message.text.split(maxsplit=1)
    token = parts[1] if len(parts) == 2 else None
    if token and message.from_user.id not in user_tokens:
        await _signup_with_invite(message.from_user, token, message)
    await message.answer("Привет! Это Trainer Bot")
    await show_menu(message.chat.id, message.from_user)


@dp.message(Command("menu"))
async def menu_cmd(message: Message):
    await show_menu(message.chat.id, message.from_user)

@dp.message(Command("help"))
async def help_cmd(message: Message):
    role = await _get_role(message.from_user)
    commands = [
        "/start",
        "/menu",
        "/help",
        "/today",
        "/future",
        "/messages",
        "/notifications",
        "/signup",
        "/report_daily",
        "/workouts",
        "/workout_get",
        "/plan_get",
        "/ex_list",
        "/ex_get",
    ]
    if role in ["coach", "superadmin"]:
        commands.extend([
            "/add_athlete",
            "/add_workout",
            "/add_set",
            "/plans",
            "/add_plan",
            "/set_contra",
            "/get_contra",
            "/invite",
            "/pending",
            "/ex_add",
            "/ex_update",
            "/ex_delete",
            "/workout_update",
            "/workout_delete",
            "/plan_update",
            "/plan_delete",
        ])
    await message.answer("Доступные команды: " + " ".join(commands))


async def exercise_menu(message: Message):
    text = (
        "Управление упражнениями:\n"
        "/ex_list - список упражнений\n"
        "/ex_add <name> <metric_type> - добавить\n"
        "/ex_update <id> <name> <metric_type> - обновить\n"
        "/ex_delete <id> - удалить\n"
        "/ex_get <id> - подробнее"
    )
    await message.answer(text)

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
                ex_name = s.exercise.name if s.exercise else str(s.exercise_id)
                await message.answer(f"{ex_name} {s.weight}×{s.reps}", reply_markup=kb)
    else:
        await message.answer("На сегодня тренировок нет.")

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



@dp.callback_query(lambda c: c.data.startswith("cmd:"))
async def menu_callback(call: CallbackQuery):
    action = call.data.split(":", 1)[1]
    if action == "today":
        await today_cmd(call.message)
    elif action == "future":
        await future_cmd(call.message)
    elif action == "help":
        await help_cmd(call.message)
    elif action == "add_athlete":
        await add_athlete_cmd(call.message)
    elif action == "add_workout":
        await add_workout_cmd(call.message)
    elif action == "add_set":
        await add_set_cmd(call.message)
    elif action == "plans":
        await list_plans_cmd(call.message)
    elif action == "invite":
        await invite_cmd(call.message)
    elif action == "exercise":
        await exercise_menu(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("set:"))
async def set_callback(call: CallbackQuery):
    _, set_id, weight, reps = call.data.split(":")
    set_id = int(set_id)
    headers = await get_auth_headers(call.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        with get_session() as session:
            obj = session.get(Set, set_id)
        if not obj:
            await call.answer("Сет не найден")
            return
        payload = {
            "workout_id": obj.workout_id,
            "exercise_id": obj.exercise_id,
            "weight": float(weight),
            "reps": int(reps),
            "order": obj.order,
        }
        url = f"/api/v1/sets/{set_id}"
        try:
            await client.patch(url, json=payload, headers=headers)
        except httpx.RequestError:
            await call.answer("Ошибка соединения")
            return
    await call.answer("Обновлено")


@dp.callback_query(lambda c: c.data.startswith("conf:"))
async def confirm_callback(call: CallbackQuery):
    _, set_id, status = call.data.split(":")
    headers = await get_auth_headers(call.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.post(f"/api/v1/sets/{set_id}/status", params={"status": status}, headers=headers)
        except httpx.RequestError:
            await call.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await call.answer("Готово")
    else:
        await call.answer("Ошибка")


@dp.callback_query(lambda c: c.data.startswith("ex:"))
async def exercise_pick(call: CallbackQuery):
    ex_id = int(call.data.split(":")[1])
    state = user_states.get(call.message.chat.id)
    if not state or state.get("cmd") != "add_set":
        await call.answer()
        return
    state["exercise_id"] = ex_id
    state["step"] = "metrics"
    await call.message.answer("Введите параметры сета. Для силовых: <вес> <повторы>. Для кардио: <км> [сек]")
    await call.answer()


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


@dp.message(Command("add_set"))
async def add_set_cmd(message: Message):
    user_states[message.chat.id] = {"cmd": "add_set", "step": "workout"}
    await message.answer("Создаём сет. Отправьте ID тренировки:")


@dp.message(Command("plans"))
async def list_plans_cmd(message: Message):
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get("/api/v1/plans/", headers=headers)
        except httpx.RequestError:
            await message.answer("Не удалось подключиться к серверу")
            return
    if resp.status_code == 200 and resp.json():
        text = "Список планов:\n" + "\n".join(f"{p['id']}: {p['title']}" for p in resp.json())
    else:
        text = "Планы отсутствуют"
    await message.answer(text)


@dp.message(Command("add_plan"))
async def add_plan_cmd(message: Message):
    user_states[message.chat.id] = {"cmd": "add_plan", "step": "title"}
    await message.answer("Введите название плана:")


@dp.message(Command("get_contra"))
async def get_contra_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Использование: /get_contra <athlete_id>")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get(f"/api/v1/athletes/{parts[1]}", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        contra = resp.json().get("contraindications") or "нет"
        await message.answer(contra)
    else:
        await message.answer("Атлет не найден")


@dp.message(Command("set_contra"))
async def set_contra_cmd(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: /set_contra <athlete_id> <текст>")
        return
    athlete_id = parts[1]
    text = parts[2]
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            res = await client.get(f"/api/v1/athletes/{athlete_id}", headers=headers)
            if res.status_code != 200:
                await message.answer("Атлет не найден")
                return
            name = res.json().get("name")
            payload = {"name": name, "contraindications": text}
            resp = await client.patch(f"/api/v1/athletes/{athlete_id}", json=payload, headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer("Обновлено")
    else:
        await message.answer("Ошибка")


@dp.message(Command("invite"))
async def invite_cmd(message: Message):
    role = await _get_role(message.from_user)
    if role is None:
        await message.answer("Не удалось подключиться к серверу")
        return
    if role not in ["coach", "superadmin"]:
        await message.answer("Недостаточно прав")
        return
    parts = message.text.split(maxsplit=1)
    payload = {}
    if len(parts) == 2:
        payload["role"] = parts[1]
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.post("/api/v1/invites/", json=payload, headers=headers)
        except httpx.RequestError:
            await message.answer("Не удалось подключиться к серверу")
            return
    if resp.status_code != 200:
        await message.answer(f"Ошибка: {resp.text}")
        return
    token = resp.json().get("invite_token")
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={token}"
    await message.answer(f"invite_token: {token}\n{link}")


@dp.message(Command("signup"))
async def signup_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Использование: /signup <token>")
        return
    if message.from_user.id in user_tokens:
        await message.answer("Вы уже зарегистрированы")
        return
    await _signup_with_invite(message.from_user, parts[1], message)
    await show_menu(message.chat.id, message.from_user)

@dp.message(Command("pending"))
async def pending_cmd(message: Message):
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get("/api/v1/sets/", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code != 200:
        await message.answer("Ошибка")
        return
    pending_sets = [s for s in resp.json() if s.get("status") == "pending"]
    if not pending_sets:
        await message.answer("Нет изменений для подтверждения")
        return
    for s in pending_sets:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Подтвердить", callback_data=f"conf:{s['id']}:confirmed"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"conf:{s['id']}:rejected")
        ]])
        await message.answer(f"set {s['id']}", reply_markup=kb)


@dp.message(Command("messages"))
async def messages_cmd(message: Message):
    parts = message.text.split(maxsplit=2)
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        if len(parts) >= 3:
            me = await client.get("/api/v1/auth/users/me", headers=headers)
            if me.status_code != 200:
                await message.answer("Ошибка аутентификации")
                return
            payload = {
                "sender_id": me.json().get("id"),
                "receiver_id": int(parts[1]),
                "text": parts[2],
            }
            try:
                resp = await client.post("/api/v1/messages/", json=payload, headers=headers)
            except httpx.RequestError:
                await message.answer("Ошибка соединения")
                return
            if resp.status_code == 200:
                await message.answer("Сообщение отправлено")
            else:
                await message.answer(f"Ошибка: {resp.text}")
        else:
            try:
                resp = await client.get("/api/v1/messages/", headers=headers)
            except httpx.RequestError:
                await message.answer("Ошибка соединения")
                return
            if resp.status_code == 200 and resp.json():
                msgs = resp.json()
                text = "\n".join(f"{m['id']}: {m['text']}" for m in msgs)
                await message.answer(text)
            else:
                await message.answer("Сообщений нет")


@dp.message(Command("notifications"))
async def notifications_cmd(message: Message):
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get("/api/v1/notifications/", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200 and resp.json():
        text = "\n".join(f"{n['id']}: {n['text']}" for n in resp.json())
        await message.answer(text)
    else:
        await message.answer("Уведомлений нет")


@dp.message(Command("ex_list"))
async def ex_list_cmd(message: Message):
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get("/api/v1/exercises/", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200 and resp.json():
        text = "\n".join(f"{e['id']}: {e['name']}" for e in resp.json())
        await message.answer(text)
    else:
        await message.answer("Упражнений нет")


@dp.message(Command("ex_add"))
async def ex_add_cmd(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: /ex_add <name> <metric_type>")
        return
    payload = {"name": parts[1], "metric_type": parts[2]}
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.post("/api/v1/exercises/", json=payload, headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer(f"Создано упражнение {resp.json().get('id')}")
    else:
        await message.answer(f"Ошибка: {resp.text}")


@dp.message(Command("ex_get"))
async def ex_get_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Использование: /ex_get <id>")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get(f"/api/v1/exercises/{parts[1]}", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer(json.dumps(resp.json(), ensure_ascii=False))
    else:
        await message.answer("Не найдено")


@dp.message(Command("ex_update"))
async def ex_update_cmd(message: Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("Использование: /ex_update <id> <name> <metric_type>")
        return
    ex_id = parts[1]
    payload = {"name": parts[2], "metric_type": parts[3]}
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.patch(f"/api/v1/exercises/{ex_id}", json=payload, headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer("Упражнение обновлено")
    else:
        await message.answer(f"Ошибка: {resp.text}")


@dp.message(Command("ex_delete"))
async def ex_delete_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Использование: /ex_delete <id>")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.delete(f"/api/v1/exercises/{parts[1]}", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer("Удалено")
    else:
        await message.answer(f"Ошибка: {resp.text}")


@dp.message(Command("workouts"))
async def workouts_cmd(message: Message):
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get("/api/v1/workouts/", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200 and resp.json():
        text = "\n".join(f"{w['id']}: {w['title']}" for w in resp.json())
        await message.answer(text)
    else:
        await message.answer("Тренировок нет")


@dp.message(Command("workout_get"))
async def workout_get_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Использование: /workout_get <id>")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get(f"/api/v1/workouts/{parts[1]}", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer(json.dumps(resp.json(), ensure_ascii=False))
    else:
        await message.answer("Не найдено")


@dp.message(Command("workout_update"))
async def workout_update_cmd(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: /workout_update <id> <json>")
        return
    wid = parts[1]
    try:
        payload = json.loads(parts[2])
    except Exception:
        await message.answer("Неверный формат JSON")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.patch(f"/api/v1/workouts/{wid}", json=payload, headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer("Тренировка обновлена")
    else:
        await message.answer(f"Ошибка: {resp.text}")


@dp.message(Command("workout_delete"))
async def workout_delete_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Использование: /workout_delete <id>")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.delete(f"/api/v1/workouts/{parts[1]}", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer("Удалено")
    else:
        await message.answer(f"Ошибка: {resp.text}")


@dp.message(Command("plan_get"))
async def plan_get_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Использование: /plan_get <id>")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get(f"/api/v1/plans/{parts[1]}", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer(json.dumps(resp.json(), ensure_ascii=False))
    else:
        await message.answer("Не найдено")


@dp.message(Command("plan_update"))
async def plan_update_cmd(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: /plan_update <id> <json>")
        return
    pid = parts[1]
    try:
        payload = json.loads(parts[2])
    except Exception:
        await message.answer("Неверный формат JSON")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.patch(f"/api/v1/plans/{pid}", json=payload, headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer("План обновлён")
    else:
        await message.answer(f"Ошибка: {resp.text}")


@dp.message(Command("plan_delete"))
async def plan_delete_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Использование: /plan_delete <id>")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.delete(f"/api/v1/plans/{parts[1]}", headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer("Удалено")
    else:
        await message.answer(f"Ошибка: {resp.text}")


@dp.message(Command("report_daily"))
async def report_daily_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Использование: /report_daily <YYYY-MM-DD>")
        return
    headers = await get_auth_headers(message.from_user)
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        try:
            resp = await client.get("/api/v1/reports/daily", params={"date": parts[1]}, headers=headers)
        except httpx.RequestError:
            await message.answer("Ошибка соединения")
            return
    if resp.status_code == 200:
        await message.answer(json.dumps(resp.json(), ensure_ascii=False))
    else:
        await message.answer(f"Ошибка: {resp.text}")


@dp.message()
async def handle_flow(message: Message):
    state = user_states.get(message.chat.id)
    if not state:
        return
    headers = await get_auth_headers(message.from_user)
    if state["cmd"] == "add_athlete":
        if state["step"] == "name":
            state["name"] = message.text.strip()
            state["step"] = "contraindications"
            await message.answer("Укажите противопоказания (или оставьте пустым):")
        elif state["step"] == "contraindications":
            payload = {"name": state["name"]}
            text = message.text.strip()
            if text:
                payload["contraindications"] = text
            async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
                try:
                    resp = await client.post("/api/v1/athletes/", json=payload, headers=headers)
                except httpx.RequestError:
                    await message.answer("Не удалось подключиться к серверу")
                    user_states.pop(message.chat.id, None)
                    await show_menu(message.chat.id, message.from_user)
                    return
            if resp.status_code == 200:
                data = resp.json()
                await message.answer(f"Атлет создан с id {data.get('id')}")
            else:
                await message.answer(f"Не удалось создать атлета: {resp.text}")
            user_states.pop(message.chat.id, None)
            await show_menu(message.chat.id, message.from_user)
    elif state["cmd"] == "add_workout":
        if state["step"] == "athlete":
            state["athlete_id"] = message.text.strip()
            state["step"] = "date"
            await message.answer("Введите дату тренировки (ГГГГ-ММ-ДД):")
        elif state["step"] == "date":
            state["date"] = message.text.strip()
            state["step"] = "time"
            await message.answer("Введите время тренировки (ЧЧ:ММ):")
        elif state["step"] == "time":
            state["time"] = message.text.strip()
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
                "time": state.get("time"),
                "type": state["type"],
                "title": state["title"],
            }
            async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
                try:
                    resp = await client.post("/api/v1/workouts/", json=payload, headers=headers)
                except httpx.RequestError:
                    await message.answer("Не удалось подключиться к серверу")
                    user_states.pop(message.chat.id, None)
                    await show_menu(message.chat.id, message.from_user)
                    return
            if resp.status_code == 200:
                data = resp.json()
                await message.answer(f"Тренировка создана с id {data.get('id')}")
            else:
                await message.answer(f"Не удалось создать тренировку: {resp.text}")
            user_states.pop(message.chat.id, None)
            await show_menu(message.chat.id, message.from_user)
    elif state["cmd"] == "add_set":
        if state["step"] == "workout":
            state["workout_id"] = int(message.text.strip())
            async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
                try:
                    resp = await client.get("/api/v1/exercises/", headers=headers)
                except httpx.RequestError:
                    await message.answer("Не удалось подключиться к серверу")
                    user_states.pop(message.chat.id, None)
                    await show_menu(message.chat.id, message.from_user)
                    return
            if resp.status_code == 200 and resp.json():
                ex_list = resp.json()
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text=e["name"], callback_data=f"ex:{e['id']}")]
                                    for e in ex_list]
                )
                state["step"] = "exercise"
                await message.answer("Выберите упражнение:", reply_markup=kb)
            else:
                await message.answer("Библиотека упражнений пуста")
                user_states.pop(message.chat.id, None)
                await show_menu(message.chat.id, message.from_user)
        elif state["step"] == "metrics":
            text = message.text.strip()
            base = {"workout_id": state["workout_id"], "exercise_id": state["exercise_id"]}
            async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
                try:
                    if "kg" in text and "×" in text:
                        sets_data = parse_strength_cell(text)
                        for item in sets_data:
                            payload = base | item
                            await client.post("/api/v1/sets/", json=payload, headers=headers)
                        await message.answer("Сеты добавлены")
                    else:
                        parts = text.split()
                        payload = base | {"order": 1}
                        if len(parts) >= 2:
                            payload["weight"] = float(parts[0])
                            payload["reps"] = int(parts[1])
                        elif len(parts) == 1:
                            payload["distance_km"] = float(parts[0])
                        resp = await client.post("/api/v1/sets/", json=payload, headers=headers)
                        if resp.status_code == 200:
                            await message.answer("Сет создан")
                        else:
                            await message.answer(f"Ошибка: {resp.text}")
                except httpx.RequestError:
                    await message.answer("Не удалось подключиться к серверу")
                    user_states.pop(message.chat.id, None)
                    await show_menu(message.chat.id, message.from_user)
                    return
            user_states.pop(message.chat.id, None)
            await show_menu(message.chat.id, message.from_user)
    elif state["cmd"] == "add_plan":
        if state["step"] == "title":
            state["title"] = message.text.strip()
            state["step"] = "notes"
            await message.answer("Введите описание плана или '-' для пропуска:")
        elif state["step"] == "notes":
            notes = message.text.strip()
            payload = {"title": state["title"]}
            if notes and notes != "-":
                payload["notes"] = notes
            async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
                try:
                    resp = await client.post("/api/v1/plans/", json=payload, headers=headers)
                except httpx.RequestError:
                    await message.answer("Не удалось подключиться к серверу")
                    user_states.pop(message.chat.id, None)
                    await show_menu(message.chat.id, message.from_user)
                    return
            if resp.status_code == 200:
                await message.answer("План создан")
            else:
                await message.answer(f"Ошибка: {resp.text}")
            user_states.pop(message.chat.id, None)
            await show_menu(message.chat.id, message.from_user)

