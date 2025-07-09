from trainer_bot.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_plan():
    res = client.post("/api/v1/plans/", json={"title": "Plan A"})
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Plan A"
    assert "id" in data
