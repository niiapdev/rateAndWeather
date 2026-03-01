import asyncio
import logging
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import TG_API_BOT
from main import get_rate

from weather import get_weather


router = Router()
dp = Dispatcher()
bot = Bot(token=TG_API_BOT)

user_data = {}



class SetInterval(StatesGroup):
    waiting_for_hours = State()

async def pereodic_sender(chat_id: int, interval_hours: int):
    while True:
        weather = get_weather()
        await asyncio.sleep(interval_hours * 3600)
        rate = get_rate()
        if rate is not None:
            await bot.send_message(
                chat_id,
                f"""
💵 Курс: {rate} RUB
🌡 Температура сейчас: {weather['current']}℃
"""
        )   



@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    weather = get_weather()
    await message.answer(
        f"""
💲 Курс доллара: {get_rate()} RUB

⛅ Прогноз Ростова-на-Дону на сегодня:
🌡 Сейчас: {weather['current']}℃
⬆ Макс: {weather['max']}℃
⬇ Мин: {weather['min']}℃
"""
    )
    
    await message.answer(
        "Через сколько часов прислать обновленную инфу?⏰\nВведи число (например: 24):"
    )
    await state.set_state(SetInterval.waiting_for_hours)

@router.message(SetInterval.waiting_for_hours, F.text)
async def process_hours(message: Message, state: FSMContext):
    try:
        hours = int(message.text)
        if hours <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите положительное целое число!Э🤬")
        return
    chat_id = message.chat.id

    if chat_id in user_data:
        user_data[chat_id]["task"].cancel()

    task = asyncio.create_task(pereodic_sender(chat_id, hours))
    user_data[chat_id] = {"interval_hours": hours, "task": task}

    await message.answer(
        f"Теперь каждые {hours}ч. ты будешь получать курс бакса/прогноза💰☁"
    )
    await state.clear()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Off bot")
