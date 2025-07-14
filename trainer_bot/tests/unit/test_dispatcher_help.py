import os
os.environ.setdefault("BOT_TOKEN", "123456:TESTTOKEN")
import asyncio
from trainer_bot.app.bots.telegram import dispatcher

class DummyUser:
    id = 1
    first_name = "T"

class DummyChat:
    id = 1

class DummyMessage:
    def __init__(self):
        self.from_user = DummyUser()
        self.chat = DummyChat()
        self.answers = []
    async def answer(self, text):
        self.answers.append(text)


def run(coro):
    return asyncio.run(coro)


def test_help_cmd_athlete(monkeypatch):
    async def fake_role(user):
        return "athlete"
    monkeypatch.setattr(dispatcher, "_get_role", fake_role)
    msg = DummyMessage()
    run(dispatcher.help_cmd(msg))
    commands = {
        "/start": "начать работу",
        "/menu": "главное меню",
        "/help": "список команд",
        "/today": "сегодняшние тренировки",
        "/future": "предстоящие тренировки",
        "/messages": "сообщения",
        "/notifications": "уведомления",
        "/signup": "регистрация по инвайту",
        "/report_daily": "отчёт за день",
        "/workouts": "список тренировок",
        "/workout_get": "подробности тренировки",
        "/plan_get": "подробности плана",
        "/ex_list": "список упражнений",
        "/ex_get": "подробности упражнения",
    }
    expected = "Доступные команды:\n" + "\n".join(
        f"{c} - {d}" for c, d in commands.items()
    )
    assert msg.answers == [expected]


def test_help_cmd_coach(monkeypatch):
    async def fake_role(user):
        return "coach"
    monkeypatch.setattr(dispatcher, "_get_role", fake_role)
    msg = DummyMessage()
    run(dispatcher.help_cmd(msg))
    commands = {
        "/start": "начать работу",
        "/menu": "главное меню",
        "/help": "список команд",
        "/today": "сегодняшние тренировки",
        "/future": "предстоящие тренировки",
        "/messages": "сообщения",
        "/notifications": "уведомления",
        "/signup": "регистрация по инвайту",
        "/report_daily": "отчёт за день",
        "/workouts": "список тренировок",
        "/workout_get": "подробности тренировки",
        "/plan_get": "подробности плана",
        "/ex_list": "список упражнений",
        "/ex_get": "подробности упражнения",
        "/add_athlete": "добавить атлета",
        "/add_workout": "добавить тренировку",
        "/add_set": "добавить сет",
        "/plans": "список планов",
        "/add_plan": "добавить план",
        "/set_contra": "задать противопоказания",
        "/get_contra": "получить противопоказания",
        "/invite": "создать инвайт",
        "/pending": "ожидающие подтверждения",
        "/ex_add": "добавить упражнение",
        "/ex_update": "обновить упражнение",
        "/ex_delete": "удалить упражнение",
        "/workout_update": "обновить тренировку",
        "/workout_delete": "удалить тренировку",
        "/plan_update": "обновить план",
        "/plan_delete": "удалить план",
    }
    expected = "Доступные команды:\n" + "\n".join(
        f"{c} - {d}" for c, d in commands.items()
    )
    assert msg.answers == [expected]


def test_show_menu_superadmin(monkeypatch):
    async def fake_role(user):
        return "superadmin"
    monkeypatch.setattr(dispatcher, "_get_role", fake_role)

    captured = {}

    async def fake_send_message(chat_id, text, reply_markup=None):
        captured["chat_id"] = chat_id
        captured["text"] = text
        captured["markup"] = reply_markup

    monkeypatch.setattr(dispatcher.bot, "send_message", fake_send_message)

    run(dispatcher.show_menu(1, DummyUser()))

    buttons = [btn.text for row in captured["markup"].inline_keyboard for btn in row]

    assert "Добавить атлета" in buttons
    assert "Инвайт" in buttons
    assert "Упражнения" in buttons
