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
    expected = "Доступные команды: " + " ".join([
        "/start", "/menu", "/help", "/today", "/future",
        "/messages", "/notifications", "/signup", "/report_daily",
        "/workouts", "/workout_get", "/plan_get", "/ex_list", "/ex_get",
    ])
    assert msg.answers == [expected]


def test_help_cmd_coach(monkeypatch):
    async def fake_role(user):
        return "coach"
    monkeypatch.setattr(dispatcher, "_get_role", fake_role)
    msg = DummyMessage()
    run(dispatcher.help_cmd(msg))
    expected = "Доступные команды: " + " ".join([
        "/start", "/menu", "/help", "/today", "/future",
        "/messages", "/notifications", "/signup", "/report_daily",
        "/workouts", "/workout_get", "/plan_get", "/ex_list", "/ex_get",
        "/add_athlete", "/add_workout", "/add_set", "/plans", "/add_plan",
        "/set_contra", "/get_contra", "/invite", "/pending", "/ex_add",
        "/ex_update", "/ex_delete", "/workout_update", "/workout_delete",
        "/plan_update", "/plan_delete",
    ])
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
