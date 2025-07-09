# Trainer Bot (MVP)

This repository contains a simplified skeleton of the "Trainer+" Telegram bot backend as described in the technical specification. The goal is to provide a minimal FastAPI application with several example endpoints and basic structure for further development.

## Quick start

### Unix/macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn trainer_bot.app.main:app --reload
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn trainer_bot.app.main:app --reload
```

### Docker (optional)

```bash
docker-compose up --build
```

Open <http://localhost:8000/docs> for the Swagger UI.
