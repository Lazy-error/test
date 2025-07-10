import os
import hashlib
import hmac
import jwt
from trainer_bot.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

BOT_TOKEN = "testtoken"
os.environ["BOT_TOKEN"] = BOT_TOKEN


def _telegram_payload(user_id: int = 1, role: str | None = None):
    data = {
        "id": user_id,
        "first_name": "Test",
        "auth_date": 1,
    }
    secret = hashlib.sha256(BOT_TOKEN.encode()).digest()
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    data["hash"] = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    if role:
        data["role"] = role
    return data


def _bot_payload(user_id: int = 2, role: str | None = None):
    data = {
        "telegram_id": user_id,
        "first_name": "Test",
        "bot_token": BOT_TOKEN,
    }
    if role:
        data["role"] = role
    return data


def test_telegram_auth_and_refresh():
    payload = _telegram_payload(role="coach")
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
    res = client.post("/api/v1/auth/bot", json=_bot_payload(role="coach"))
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_change_user_role():
    # register normal user
    res_user = client.post("/api/v1/auth/telegram", json=_telegram_payload(user_id=10, role="athlete"))
    user_id = int(jwt.decode(res_user.json()["access_token"], "secret", algorithms=["HS256"])["sub"])
    # register superadmin
    admin_tokens = client.post("/api/v1/auth/bot", json=_bot_payload(user_id=20, role="superadmin")).json()
    headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}
    res = client.patch(f"/api/v1/auth/users/{user_id}/role", json={"role": "coach"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["role"] == "coach"
