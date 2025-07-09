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

### PostgreSQL with Docker Compose

The default `DATABASE_URL` expects a PostgreSQL server. To start the bundled
database using Docker Compose:

```bash
docker-compose up -d db
```

This launches a PostgreSQL instance listening on port `5432` with the
`trainer/trainer` user/password combination. The database name is `trainer`.

To use TimescaleDB features, enable the extension after the container starts:

```bash
docker exec -it test-db-1 psql -U trainer -d trainer -c "CREATE EXTENSION IF NOT EXISTS timescaledb"
```

Replace `test-db-1` with the name of your running container if it differs.

Open <http://localhost:8000/docs> for the Swagger UI.

### Running the Telegram bot

The repository includes a minimal Telegram bot that responds to `/start`.
Set your bot token in the `BOT_TOKEN` environment variable and run the helper
script:

```bash
export BOT_TOKEN="your-telegram-token"
python run_bot.py
```

After starting the script the bot will begin polling Telegram and will
reply with `Hello! This is Trainer Bot` when you send the `/start` command.
