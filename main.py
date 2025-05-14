import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config
from database import create_table
import pills, common


async def main():
    await create_table()

    bot = Bot(token=config("TELEGRAM_TOKEN"))
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(pills.router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(pills.check_pills, 'interval', minutes=1, args=[bot])
    scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())