import os
import hashlib
import hmac
from trainer_bot.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

BOT_TOKEN = "testtoken"
os.environ["BOT_TOKEN"] = BOT_TOKEN


def _telegram_payload(user_id: int = 1):
    data = {
        "id": user_id,
        "first_name": "Test",
        "auth_date": 1,
    }
    secret = hashlib.sha256(BOT_TOKEN.encode()).digest()
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    data["hash"] = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    return data


def _bot_payload(user_id: int = 2):
    return {
        "telegram_id": user_id,
        "first_name": "Test",
        "bot_token": BOT_TOKEN,
    }


def test_telegram_auth_and_refresh():
    payload = _telegram_payload()
    res = client.post("/api/v1/auth/telegram", json=payload)
    assert res.status_code == 200
    tokens = res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    res2 = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert res2.status_code == 200
    new_tokens = res2.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]
    assert "access_token" in new_tokens


def test_bot_auth():
    res = client.post("/api/v1/auth/bot", json=_bot_payload())
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
