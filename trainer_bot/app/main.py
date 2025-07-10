from fastapi import FastAPI

from .api import athletes, workouts, sets, plans, reports, notifications, messages, telegram, auth, protected, exercises

app = FastAPI(title="Trainer Bot API")

app.include_router(athletes.router, prefix="/api/v1")
app.include_router(workouts.router, prefix="/api/v1")
app.include_router(sets.router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")
app.include_router(exercises.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(telegram.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(protected.router, prefix="/api/v1")

@app.get("/ping")
async def ping():
    return {"status": "ok"}
