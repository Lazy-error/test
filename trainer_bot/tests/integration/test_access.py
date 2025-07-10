import os
os.environ["BOT_TOKEN"] = "123456:TESTTOKEN"

import hashlib
import hmac
import jwt
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


def _auth_headers(role="athlete", user_id: int = 5):
    res = client.post("/api/v1/auth/telegram", json=_telegram_payload(user_id=user_id, role=role))
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_athlete_cannot_issue_invite():
    headers = _auth_headers(role="athlete")
    res = client.post("/api/v1/invites/", json={}, headers=headers)
    assert res.status_code == 403


def test_non_admin_cannot_change_role():
    headers = _auth_headers(role="coach", user_id=10)
    res = client.post("/api/v1/auth/telegram", json=_telegram_payload(user_id=20, role="athlete"))
    token = res.json()["access_token"]
    target_uid = int(jwt.decode(token, "secret", algorithms=["HS256"])["sub"])
    res = client.patch(
        f"/api/v1/auth/users/{target_uid}/role", json={"role": "coach"}, headers=headers
    )
    assert res.status_code == 403


