# Trainer Bot (MVP)

This repository contains a simplified skeleton of the "Trainer+" Telegram bot backend as described in the technical specification. The goal is to provide a minimal FastAPI application with several example endpoints and basic structure for further development.

## Quick start

### Unix/macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="your-telegram-token"
export DATABASE_URL="postgresql://trainer:trainer@localhost:5432/trainer"
uvicorn trainer_bot.app.main:app --reload
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set BOT_TOKEN="your-telegram-token"
set DATABASE_URL="postgresql://trainer:trainer@localhost:5432/trainer"
uvicorn trainer_bot.app.main:app --reload
```

### Docker

```bash
docker-compose up --build
```
This command starts PostgreSQL, Redis and the FastAPI app. Set `BOT_TOKEN` in
your environment so the backend can authorize Telegram users before running.

### PostgreSQL

The application requires a running PostgreSQL server. The default
`DATABASE_URL` is `postgresql://trainer:trainer@localhost:5432/trainer`. If you
use Docker Compose, the database is created automatically. Otherwise make sure
the `trainer` database and user exist before starting the app.

To enable TimescaleDB features in the Docker container run:

```bash
docker exec -it test-db-1 psql -U trainer -d trainer -c "CREATE EXTENSION IF NOT EXISTS timescaledb"
```

Open <http://localhost:8000/docs> for the Swagger UI once the service is running.

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

Exercises can also be managed interactively. Choose **Новое упражнение** in
the *Упражнения* menu or send `/ex_add` without arguments. The bot will ask for
the exercise name followed by its metric type (`strength` or `cardio`).
To update an existing exercise send `/ex_update <id>` and follow the prompts to
change its name and metric type.

### Authorizing via Telegram

At the first interaction the bot requests an API token from the backend by
calling `/api/v1/auth/bot`. This request includes your Telegram profile and
the `BOT_TOKEN`. Make sure the backend runs with the same `BOT_TOKEN`; otherwise
authentication fails and subsequent commands return `403 FORBIDDEN`. When the
token is issued a new user with the `athlete` role is created in the database.
The available roles are `coach`, `athlete` and `superadmin`. Any endpoint that
requires a different role will return `403` until the user's role is updated.

### Inviting users

Coaches can generate invitation links for new athletes with:

```text
/invite [role]
```


The bot responds with an `invite_token` and a deep link like
`https://t.me/<botname>?start=<token>`. A new user can follow this link or send
`/signup <token>` to register. The bot submits the token to `/api/v1/invites/bot`
and stores the received `access_token` for future requests.

### Time zone

The scheduler uses the `TZ` environment variable to determine the bot's time
zone. If unset, the application defaults to **Europe/Moscow**.

### Running tests

Install the development requirements first so that packages such as
`testing.postgresql` are available:

```bash
pip install -r requirements.txt
```

The test suite expects a Telegram bot token via the `BOT_TOKEN` environment
variable. Any value will work for local testing:

```bash
export BOT_TOKEN=testtoken
pytest
```
