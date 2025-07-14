import os
os.environ.setdefault("BOT_TOKEN", "123456:TESTTOKEN")
import asyncio
from trainer_bot.app.bots.telegram import dispatcher
from aiogram.types import InlineKeyboardMarkup

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
        self.text = "/invite"
    async def answer(self, text, reply_markup=None):
        self.answers.append((text, reply_markup))

class DummyCallback:
    def __init__(self, data):
        self.data = data
        self.from_user = DummyUser()
        self.message = DummyMessage()
        self.callback_answers = []
    async def answer(self, text=None):
        self.callback_answers.append(text)

def run(coro):
    return asyncio.run(coro)


def test_invite_cmd_interactive(monkeypatch):
    async def fake_role(user):
        return "coach"
    monkeypatch.setattr(dispatcher, "_get_role", fake_role)

    msg = DummyMessage()

    run(dispatcher.invite_cmd(msg))

    state = dispatcher.user_states.get(msg.chat.id)
    assert state == {"cmd": "invite", "step": "role"}
    assert msg.answers, "no answer sent"
    text, markup = msg.answers[0]
    assert isinstance(markup, InlineKeyboardMarkup)
    buttons = [btn.callback_data for row in markup.inline_keyboard for btn in row]
    assert "invite_role:athlete" in buttons
    assert "invite_role:coach" in buttons


def test_invite_role_callback(monkeypatch):
    async def fake_headers(user):
        return {"Authorization": "Bearer X"}

    class DummyClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def post(self, url, json=None, headers=None):
            assert json == {"role": "athlete"}
            return type("Resp", (), {"status_code": 200, "json": lambda self: {"invite_token": "TOK"}})()

    async def fake_get_me():
        return type("B", (), {"username": "bot"})()

    monkeypatch.setattr(dispatcher, "get_auth_headers", fake_headers)
    monkeypatch.setattr(dispatcher.httpx, "AsyncClient", lambda **kw: DummyClient())
    monkeypatch.setattr(dispatcher.bot, "get_me", fake_get_me)

    shown = {}

    async def fake_show_menu(chat_id, tg_user=None):
        shown["called"] = True

    monkeypatch.setattr(dispatcher, "show_menu", fake_show_menu)

    dispatcher.user_states[1] = {"cmd": "invite", "step": "role"}
    cb = DummyCallback("invite_role:athlete")

    run(dispatcher.invite_role(cb))

    assert dispatcher.user_states.get(1) is None
    assert cb.message.answers[0][0].startswith("invite_token: TOK")
    assert shown.get("called") is True
