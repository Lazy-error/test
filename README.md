# Trainer Bot (MVP)

This repository contains a simplified skeleton of the "Trainer+" Telegram bot backend as described in the technical specification. The goal is to provide a minimal FastAPI application with several example endpoints and basic structure for further development.

## Quick start

### Unix/macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="your-telegram-token"
uvicorn trainer_bot.app.main:app --reload
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set BOT_TOKEN="your-telegram-token"
uvicorn trainer_bot.app.main:app --reload
```

### Docker (optional)

```bash
docker-compose up --build
```
The compose file expects `BOT_TOKEN` to be set in your environment so the
backend can authorize Telegram users.

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

Before starting the backend, export the same `BOT_TOKEN` that the bot uses so
`/api/v1/auth/bot` can authenticate:

```bash
export BOT_TOKEN="your-telegram-token"
uvicorn trainer_bot.app.main:app --reload
```

Open <http://localhost:8000/docs> for the Swagger UI.

### Running the Telegram bot

The repository includes a minimal Telegram bot that responds to `/start`.
Set your bot token in the `BOT_TOKEN` environment variable and run the helper
script. The bot sends API requests to `http://localhost:8000` by default; set
`API_BASE_URL` to override this if your backend runs elsewhere:

```bash
export BOT_TOKEN="your-telegram-token"
python run_bot.py
```

After starting the script the bot will begin polling Telegram and will
reply with `Привет! Это Trainer Bot` when you send the `/start` command.
The `/start` or `/menu` command displays quick action buttons so a trainer can
navigate the bot without typing raw API requests.

The bot now supports interactive creation of athletes and workouts. Use
`/add_athlete` or `/add_workout` from Telegram and follow the prompts.
When adding a workout you will be asked for the athlete ID (a numeric
identifier), the workout date in `YYYY-MM-DD` format, a type such as
`strength` or `cardio`, and a short title. After the object is created the
bot returns to the main menu.

### Authorizing via Telegram

At the first interaction the bot requests an API token from the backend by
calling `/api/v1/auth/bot`. This request includes your Telegram profile and
the `BOT_TOKEN`. Make sure the backend runs with the same `BOT_TOKEN`; otherwise
authentication fails and subsequent commands return `403 FORBIDDEN`. When the
token is issued a new user with the `athlete` role is created in the database.
The available roles are `coach`, `athlete` and `superadmin`. Any endpoint that
requires a different role will return `403` until the user's role is updated.

### Using API commands via Telegram

The bot exposes an `/api` command so the trainer can call any backend endpoint
directly from Telegram. Usage:

```text
/api <method> <path> [json]
```

Example:

```text
/api get /api/v1/workouts
```

By default the bot obtains an access token automatically using your Telegram
account through the `/api/v1/auth/bot` endpoint. You can override the token by
setting `TRAINER_API_TOKEN` with a valid bearer token.

### Time zone

The scheduler uses the `TZ` environment variable to determine the bot's time
zone. If unset, the application defaults to **Europe/Moscow**.

### Running tests

The test suite expects a Telegram bot token via the `BOT_TOKEN` environment
variable. Any value will work for local testing:

```bash
export BOT_TOKEN=testtoken
pytest
```
