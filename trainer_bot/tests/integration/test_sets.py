from trainer_bot.app.main import app
from fastapi.testclient import TestClient
import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
if os.path.exists("test.db"):
    os.remove("test.db")

client = TestClient(app)

def test_create_set():
    # Create athlete and workout first
    ath = client.post("/api/v1/athletes/", json={"name": "Bob"}).json()
    wo = client.post("/api/v1/workouts/", json={
        "athlete_id": ath["id"],
        "date": "2025-07-10",
        "type": "strength",
        "title": "Test",
        "notes": ""
    }).json()
    res = client.post("/api/v1/sets/", json={
        "workout_id": wo["id"],
        "exercise": "Bench",
        "weight": 100,
        "reps": 5,
        "order": 1
    })
    assert res.status_code == 200
    data = res.json()
    assert data["exercise"] == "Bench"
