import asyncio
from trainer_bot.app.bots.telegram.dispatcher import bot, dp

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
