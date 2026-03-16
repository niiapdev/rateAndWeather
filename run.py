import asyncio
import logging
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


from config import TG_API_BOT

from main import get_rate
from weather import get_weather
from keyboards import main_kkb
from keyboards import select_number

router = Router()
dp = Dispatcher()
bot = Bot(token=TG_API_BOT)

user_data = {}

task_input = 'Через сколько часов прислать обновленную инфу?⏰\n\nНажми на кнопку или↔️\nВведи число (например: 24):'

class SetInterval(StatesGroup):
    waiting_for_hours = State()

async def periodic_sender(chat_id: int, interval_hours: int):
    try:
        while True:
            await asyncio.sleep(interval_hours * 36)
            weather = get_weather()
            rate = get_rate()
            if rate is not None:
                await bot.send_message(
                chat_id,
                f"""
💵 Доллар: {rate['usd']} RUB
💴 Йены: 0.{rate['jpy']} RUB
🌡 Температура сейчас: {weather['current']}℃
"""
        )

    except asyncio.CancelledError:
        return

async def send_rate_weather(message: Message):
    weather = get_weather()
    rate = get_rate()
    await message.answer(
        f"""
💲 Курс доллара: {rate['usd']} RUB
💴 Курс йены: 0.{rate['jpy']} RUB

⛅ Прогноз Ростова-на-Дону на сегодня:
🌡 Сейчас: {weather['current']}℃
⬆ Макс: {weather['max']}℃
⬇ Мин: {weather['min']}℃
""",
    reply_markup=main_kkb()
    )

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await send_rate_weather(message)
    await message.answer(task_input,
    reply_markup = select_number()
    )
    await state.set_state(SetInterval.waiting_for_hours)

@router.message(F.text == 'Запросить курс/прогноз сейчас')
async def cmd_wr(message: Message, state: FSMContext):
    await send_rate_weather(message)
    await message.answer(task_input,
    reply_markup = select_number()
    )
    await state.set_state(SetInterval.waiting_for_hours)

@router.message(F.text == 'Отменить рассылку')
async def cmd_clear(message: Message):
    chat_id = message.chat.id
    if chat_id in user_data:
        user_data[chat_id]["task"].cancel()
        del user_data[chat_id]
        await message.answer('Рассылка была успешно отменена🛑')
    else:
        await message.answer('Активной рассылки у вас нет!❌')


@router.callback_query(SetInterval.waiting_for_hours, F.data.isdigit())
async def hours_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    hours = int(callback.data)

    chat_id2 = callback.message.chat.id

    if chat_id2 in user_data:
        user_data[chat_id2]["task"].cancel()

    task = asyncio.create_task(periodic_sender(chat_id2, hours))
    user_data[chat_id2] = {"interval_hours": hours, "task": task}

    await callback.message.answer(
        f"Теперь каждые {hours}ч. ты будешь получать курс бакса/прогноза💰☁"
    )
    await state.clear()

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

    task = asyncio.create_task(periodic_sender(chat_id, hours))
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
