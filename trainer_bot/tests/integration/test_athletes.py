import os
import hashlib
import hmac
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


def _auth_headers():
    res = client.post("/api/v1/auth/telegram", json=_telegram_payload(role="coach"))
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_athlete():
    headers = _auth_headers()
    payload = {"name": "John", "contraindications": "asthma"}
    res = client.post("/api/v1/athletes/", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "John"
    assert data["contraindications"] == "asthma"
    assert "id" in data
