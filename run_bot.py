import asyncio
from trainer_bot.app.bots.telegram.dispatcher import bot, dp
from trainer_bot.app.services.scheduler import setup_scheduler

async def main():
    setup_scheduler()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
