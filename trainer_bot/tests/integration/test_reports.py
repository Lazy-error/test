from trainer_bot.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_daily_report():
    client.post("/api/v1/workouts/", json={"athlete_id": 1, "date": "2025-07-10", "type": "strength", "title": "W"})
    res = client.get("/api/v1/reports/daily", params={"date": "2025-07-10"})
    assert res.status_code == 200
    data = res.json()
    assert data["date"] == "2025-07-10"
    assert len(data["workouts"]) >= 1
