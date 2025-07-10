import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


@pytest.fixture(autouse=True)
def _bot_token_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "123456:TESTTOKEN")
