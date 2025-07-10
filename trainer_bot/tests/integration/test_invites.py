import os
os.environ["BOT_TOKEN"] = "123456:TESTTOKEN"

import hashlib
import hmac
from trainer_bot.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
BOT_TOKEN = "123456:TESTTOKEN"


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


def _coach_headers():
    res = client.post("/api/v1/auth/telegram", json={**_telegram_payload(1), "role": "coach"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_invite_flow():
    headers = _coach_headers()
    res = client.post("/api/v1/invites/", json={}, headers=headers)
    assert res.status_code == 200
    token = res.json()["invite_token"]

    payload = {
        "telegram_id": 50,
        "first_name": "Invited",
        "bot_token": BOT_TOKEN,
        "invite_token": token,
    }
    res2 = client.post("/api/v1/invites/bot", json=payload)
    assert res2.status_code == 200

    # reuse should fail
    res3 = client.post("/api/v1/invites/bot", json=payload)
    assert res3.status_code == 400
