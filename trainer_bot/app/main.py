from fastapi import FastAPI

from .api import athletes, workouts

app = FastAPI(title="Trainer Bot API")

app.include_router(athletes.router, prefix="/api/v1")
app.include_router(workouts.router, prefix="/api/v1")

@app.get("/ping")
async def ping():
    return {"status": "ok"}
