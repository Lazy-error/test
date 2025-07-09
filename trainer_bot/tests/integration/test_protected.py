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


def _auth_headers():
    res = client.post("/api/v1/auth/telegram", json=_telegram_payload())
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_protected_requires_auth():
    res = client.get("/api/v1/protected/ping")
    assert res.status_code == 403


def test_protected_ping():
    headers = _auth_headers()
    res = client.get("/api/v1/protected/ping", headers=headers)
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "user_id": 1}
