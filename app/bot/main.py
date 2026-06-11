import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from app.bot.admin_ui import router as admin_router
from app.bot.handlers import router as user_router

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


async def main():
    print("TOKEN:", TOKEN)

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(user_router)
    dp.include_router(admin_router)

    print("Bot is starting...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())