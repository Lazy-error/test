FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY trainer_bot trainer_bot
CMD ["uvicorn", "trainer_bot.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
