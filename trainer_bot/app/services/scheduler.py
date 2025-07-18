from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import pytz
import os

from ..models import Workout
from .db import get_session
from ..bots.telegram.dispatcher import bot

async def late_report_reminder():
    tz = pytz.timezone(os.getenv("TZ", "Europe/Moscow"))
    today = datetime.now(tz).date()
    with get_session() as session:
        workouts = session.query(Workout).filter(Workout.date == today).all()
    missing = []
    for w in workouts:
        if not w.sets or any(s.status != "confirmed" for s in w.sets):
            missing.append(w.title)
    if not missing:
        return
    text = "Missing reports: " + ", ".join(missing)
    athlete_chat = os.getenv("ATHLETE_CHAT_ID")
    if athlete_chat:
        await _send(athlete_chat, text)

async def incomplete_today():
    tz = pytz.timezone(os.getenv("TZ", "Europe/Moscow"))
    today = datetime.now(tz).date()
    with get_session() as session:
        workouts = session.query(Workout).filter(Workout.date == today).all()
    missing = []
    for w in workouts:
        if not w.sets or any(s.status != "confirmed" for s in w.sets):
            missing.append(w.title)
    if not missing:
        return
    text = "Incomplete workouts: " + ", ".join(missing)
    trainer_chat = os.getenv("TRAINER_CHAT_ID")
    if trainer_chat:
        await _send(trainer_chat, text)

scheduler = AsyncIOScheduler()

async def _send(chat_id: str, text: str):
    await bot.send_message(chat_id, text)

async def workout_reminder(workout_id: int):
    with get_session() as session:
        w = session.get(Workout, workout_id)
    if not w:
        return
    text = f"Reminder: workout '{w.title}' in one hour"
    trainer_chat = os.getenv("TRAINER_CHAT_ID")
    athlete_chat = os.getenv("ATHLETE_CHAT_ID")
    if trainer_chat:
        await _send(trainer_chat, text)
    if athlete_chat:
        await _send(athlete_chat, text)

def schedule_workout_reminder(workout: Workout):
    tz = pytz.timezone(os.getenv("TZ", "Europe/Moscow"))
    w_dt = datetime.combine(workout.date, workout.time or datetime.min.time())
    dt = tz.localize(w_dt) - timedelta(hours=1)
    scheduler.add_job(workout_reminder, 'date', run_date=dt, args=[workout.id])

async def daily_reminder():
    tz = pytz.timezone(os.getenv("TZ", "Europe/Moscow"))
    tomorrow = datetime.now(tz).date() + timedelta(days=1)
    with get_session() as session:
        workouts = session.query(Workout).filter(Workout.date == tomorrow).all()
    if not workouts:
        return
    text = "Tomorrow's workouts:\n" + "\n".join(w.title for w in workouts)
    trainer_chat = os.getenv("TRAINER_CHAT_ID")
    athlete_chat = os.getenv("ATHLETE_CHAT_ID")
    if trainer_chat:
        await _send(trainer_chat, text)
    if athlete_chat:
        await _send(athlete_chat, text)


def setup_scheduler():
    tz = pytz.timezone(os.getenv("TZ", "Europe/Moscow"))
    scheduler.configure(timezone=tz)
    scheduler.add_job(daily_reminder, 'cron', hour=20, minute=0)
    scheduler.add_job(incomplete_today, 'cron', hour=20, minute=0)
    scheduler.add_job(late_report_reminder, 'cron', hour=23, minute=59)
    with get_session() as session:
        workouts = session.query(Workout).all()
        for w in workouts:
            schedule_workout_reminder(w)
    scheduler.start()

