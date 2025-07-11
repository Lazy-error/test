import os
os.environ["BOT_TOKEN"] = "123456:TESTTOKEN"

import hashlib
import hmac
from trainer_bot.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
BOT_TOKEN = "123456:TESTTOKEN"


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


def test_deactivate_and_activate_athlete():
    headers = _auth_headers()
    payload = {"name": "Jane"}
    res = client.post("/api/v1/athletes/", json=payload, headers=headers)
    athlete_id = res.json()["id"]

    res = client.post(f"/api/v1/athletes/{athlete_id}/deactivate", headers=headers)
    assert res.status_code == 200
    assert res.json()["is_active"] is False

    res = client.get("/api/v1/athletes/", headers=headers)
    assert all(a["id"] != athlete_id for a in res.json())

    res = client.get("/api/v1/athletes/?include_inactive=true", headers=headers)
    assert any(a["id"] == athlete_id for a in res.json())

    res = client.post(f"/api/v1/athletes/{athlete_id}/activate", headers=headers)
    assert res.status_code == 200
    assert res.json()["is_active"] is True

    res = client.get("/api/v1/athletes/", headers=headers)
    assert any(a["id"] == athlete_id for a in res.json())
