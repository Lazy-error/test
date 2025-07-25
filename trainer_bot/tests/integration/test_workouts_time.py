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


def test_create_workout_with_time():
    headers = _auth_headers()
    payload = {"athlete_id": 1, "date": "2025-01-02", "time": "10:30", "type": "strength", "title": "W"}
    res = client.post("/api/v1/workouts/", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["time"] == "10:30:00"


def test_schedule_called_on_create(monkeypatch):
    headers = _auth_headers()
    payload = {"athlete_id": 1, "date": "2025-01-05", "time": "09:00", "type": "strength", "title": "S"}
    called = {}

    def fake_schedule(w):
        called["id"] = w.id

    monkeypatch.setattr("trainer_bot.app.api.workouts.schedule_workout_reminder", fake_schedule)
    res = client.post("/api/v1/workouts/", json=payload, headers=headers)
    assert res.status_code == 200
    assert "id" in called


def test_schedule_called_on_update(monkeypatch):
    headers = _auth_headers()
    payload = {"athlete_id": 1, "date": "2025-01-06", "time": "08:00", "type": "strength", "title": "U"}
    res = client.post("/api/v1/workouts/", json=payload, headers=headers)
    wid = res.json()["id"]
    called = {}

    def fake_schedule(w):
        called["id"] = w.id

    monkeypatch.setattr("trainer_bot.app.api.workouts.schedule_workout_reminder", fake_schedule)
    res = client.patch(f"/api/v1/workouts/{wid}", json=payload, headers=headers)
    assert res.status_code == 200
    assert called["id"] == wid


def test_get_and_delete_workout():
    headers = _auth_headers()
    payload = {"athlete_id": 1, "date": "2025-01-07", "type": "strength", "title": "D"}
    res = client.post("/api/v1/workouts/", json=payload, headers=headers)
    wid = res.json()["id"]

    res = client.get(f"/api/v1/workouts/{wid}", headers=headers)
    assert res.status_code == 200

    res = client.delete(f"/api/v1/workouts/{wid}", headers=headers)
    assert res.json()["status"] == "deleted"
