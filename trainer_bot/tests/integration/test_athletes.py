from trainer_bot.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_athlete():
    res = client.post("/api/v1/athletes/", json={"name": "John"})
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "John"
    assert "id" in data
