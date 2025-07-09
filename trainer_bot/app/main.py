from fastapi import FastAPI

from .api import athletes, workouts, sets
from .services.db import init_db

app = FastAPI(title="Trainer Bot API")

init_db()

app.include_router(athletes.router, prefix="/api/v1")
app.include_router(workouts.router, prefix="/api/v1")
app.include_router(sets.router, prefix="/api/v1")

@app.get("/ping")
async def ping():
    return {"status": "ok"}
