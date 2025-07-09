# Trainer Bot (MVP)

This repository contains a minimal implementation of the "Trainer+" Telegram bot backend. It exposes a FastAPI server with SQLite storage and a tiny Telegram bot using aiogram.

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn trainer_bot.app.main:app --reload
```

The first start creates a local `trainer.db` SQLite file.

To run the Telegram bot locally set `BOT_TOKEN` environment variable and start the dispatcher:

```bash
python -m trainer_bot.app.bots.telegram.dispatcher
```

Open <http://localhost:8000/docs> for the Swagger UI.
