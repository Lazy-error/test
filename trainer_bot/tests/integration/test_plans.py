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

def test_create_plan():
    headers = _auth_headers()
    res = client.post("/api/v1/plans/", json={"title": "Plan A"}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Plan A"
    assert "id" in data


def test_plan_crud():
    headers = _auth_headers()
    res = client.post("/api/v1/plans/", json={"title": "Plan B"}, headers=headers)
    plan_id = res.json()["id"]

    res = client.get("/api/v1/plans/", headers=headers)
    assert any(p["id"] == plan_id for p in res.json())

    res = client.get(f"/api/v1/plans/{plan_id}", headers=headers)
    assert res.status_code == 200

    res = client.patch(f"/api/v1/plans/{plan_id}", json={"title": "Plan C"}, headers=headers)
    assert res.json()["title"] == "Plan C"

    res = client.delete(f"/api/v1/plans/{plan_id}", headers=headers)
    assert res.json()["status"] == "deleted"
