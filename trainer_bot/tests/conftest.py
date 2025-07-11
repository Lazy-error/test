import os
import sys
from pathlib import Path
import pytest
import testing.postgresql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    _POSTGRES = testing.postgresql.Postgresql()
    os.environ["DATABASE_URL"] = _POSTGRES.url()

    from trainer_bot.app.services import db as db_module

    db_module.engine = create_engine(_POSTGRES.url())
    db_module.SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_module.engine
    )
    db_module.Base.metadata.create_all(bind=db_module.engine)
    _POSTGRES_ERROR = None
except Exception as exc:  # pragma: no cover - depends on environment
    _POSTGRES = None
    _POSTGRES_ERROR = str(exc)


def pytest_configure(config):
    if _POSTGRES is None:
        pytest.skip(f"PostgreSQL not available: {_POSTGRES_ERROR}", allow_module_level=True)


def pytest_unconfigure(config):
    if _POSTGRES is not None:
        _POSTGRES.stop()


@pytest.fixture(autouse=True)
def _bot_token_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "123456:TESTTOKEN")
