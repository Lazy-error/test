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


def _auth_headers(role="coach", user_id: int = 1):
    res = client.post("/api/v1/auth/telegram", json=_telegram_payload(user_id=user_id, role=role))
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_set():
    headers = _auth_headers()
    res = client.post("/api/v1/exercises/", json={"name": "Bench", "metric_type": "strength"}, headers=headers)
    ex_id = res.json()["id"]
    res = client.post("/api/v1/workouts/", json={"athlete_id": 1, "date": "2025-01-01", "type": "strength", "title": "A"}, headers=headers)
    wid = res.json()["id"]
    payload = {"workout_id": wid, "exercise_id": ex_id, "weight": 50, "reps": 5, "order": 1}
    res = client.post("/api/v1/sets/", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["workout_id"] == wid
    assert data["exercise_id"] == ex_id


def test_create_cardio_set():
    headers = _auth_headers()
    ex = client.post("/api/v1/exercises/", json={"name": "Run", "metric_type": "cardio"}, headers=headers)
    ex_id = ex.json()["id"]
    res = client.post(
        "/api/v1/workouts/",
        json={"athlete_id": 1, "date": "2025-01-02", "type": "cardio", "title": "Run"},
        headers=headers,
    )
    wid = res.json()["id"]
    payload = {"workout_id": wid, "exercise_id": ex_id, "distance_km": 5, "duration_sec": 1500, "order": 1}
    res = client.post("/api/v1/sets/", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["distance_km"] == 5
    assert data["duration_sec"] == 1500


def test_create_set_with_rest():
    headers = _auth_headers()
    res = client.post("/api/v1/exercises/", json={"name": "Pull", "metric_type": "strength"}, headers=headers)
    ex_id = res.json()["id"]
    res = client.post(
        "/api/v1/workouts/",
        json={"athlete_id": 1, "date": "2025-01-04", "type": "strength", "title": "R"},
        headers=headers,
    )
    wid = res.json()["id"]
    payload = {"workout_id": wid, "exercise_id": ex_id, "weight": 60, "reps": 5, "order": 1, "rest_sec": 90}
    res = client.post("/api/v1/sets/", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["rest_sec"] == 90


def test_pending_edit_by_athlete_and_confirm():
    coach_headers = _auth_headers()
    ex = client.post("/api/v1/exercises/", json={"name": "Press", "metric_type": "strength"}, headers=coach_headers)
    ex_id = ex.json()["id"]
    res = client.post(
        "/api/v1/workouts/",
        json={"athlete_id": 1, "date": "2025-01-03", "type": "strength", "title": "S"},
        headers=coach_headers,
    )
    wid = res.json()["id"]
    res = client.post(
        "/api/v1/sets/",
        json={"workout_id": wid, "exercise_id": ex_id, "weight": 40, "reps": 5, "order": 1},
        headers=coach_headers,
    )
    set_id = res.json()["id"]
    athlete_headers = _auth_headers(role="athlete", user_id=99)
    res = client.patch(
        f"/api/v1/sets/{set_id}",
        json={"weight": 42},
        headers=athlete_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending"
    # coach confirms
    res = client.post(
        f"/api/v1/sets/{set_id}/status",
        params={"status": "confirmed"},
        headers=coach_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "confirmed"
