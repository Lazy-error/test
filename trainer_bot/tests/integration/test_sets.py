from trainer_bot.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_create_set():
    # create workout first
    res = client.post("/api/v1/workouts/", json={"athlete_id": 1, "date": "2025-01-01", "type": "strength", "title": "A"})
    wid = res.json()["id"]
    res = client.post("/api/v1/sets/", json={"workout_id": wid, "exercise": "Bench", "weight": 50, "reps": 5, "order": 1})
    assert res.status_code == 200
    data = res.json()
    assert data["workout_id"] == wid
    assert data["exercise"] == "Bench"
