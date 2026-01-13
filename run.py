import asyncio
import logging
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram import Router
from config import TG_API_BOT
from main import usd_rate

router = Router()
dp = Dispatcher()
bot = Bot(token=TG_API_BOT)


@router.message(CommandStart())
async def cmd_start(message: Message):
    for i in range(1):
        await message.answer(f"Курс aдоллараa: {usd_rate:.2f} RUB")
        await asyncio.sleep(1)


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Off bot")
