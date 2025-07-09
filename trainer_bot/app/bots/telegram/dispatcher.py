from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
import os

API_TOKEN = os.getenv("BOT_TOKEN", "test-token")

bot = Bot(API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello! This is Trainer Bot")
