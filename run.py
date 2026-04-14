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
from db import add_task
from datetime import time
from db import get_active_tasks
from datetime import datetime
from zoneinfo import ZoneInfo
from db import deactivate_task

router = Router()
dp = Dispatcher()
bot = Bot(token=TG_API_BOT)


task_input = 'В какое время дня отправлять тебе обновленную инфу?⏰\n\nНажми на кнопку или↔️\nВведи число (например: 24):'

class SetInterval(StatesGroup):
    waiting_for_hours = State()

async def scheduler():
    while True:
        now = datetime.now(ZoneInfo('Europe/Moscow'))
        current_time = now.time().replace(second=0, microsecond=0)
        tasks = await get_active_tasks()
        for task in tasks:
            if task['send_time'] == current_time:
                chat_id = task['chat_id']
                weather = get_weather()
                rate = get_rate()
                await bot.send_message(
                    chat_id,
                    f"""
💵 Доллар: {rate['usd']} RUB
💴 Йены: 0.{rate['jpy']} RUB
🌡 Температура сейчас: {weather['current']}℃
                """
                )

        await asyncio.sleep(50)

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
    #if chat_id in user_data:
        #user_data[chat_id]["task"].cancel()
        #del user_data[chat_id]
    result = await deactivate_task(chat_id)
    if result == 'UPDATE 0':
        await message.answer('Активной рассылки у вас нет!❌')
    else:
        #await message.answer('Активной рассылки у вас нет!❌')
        await message.answer('Рассылка была успешно отменена🛑')


@router.callback_query(SetInterval.waiting_for_hours, F.data.isdigit())
async def hours_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

    hours = int(callback.data) #получ число часов от юзера
    chat_id = callback.message.chat.id #получ id user

    send_time = time(hours, 0)

    #if chat_id in user_data:
        #user_data[chat_id]["task"].cancel()

    await add_task(chat_id, send_time) #сохр задач в бд вместо фон задачи
    #task = asyncio.create_task(periodic_sender(chat_id, hours))
    #user_data[chat_id] = {"interval_hours": hours, "task": task}

    await callback.message.answer(
        f"Теперь каждый день в {hours}:00 ты будешь получать курс бакса/прогноза💰☁"
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

    send_time = time(hours, 0)
    #if chat_id in user_data:
        #user_data[chat_id]["task"].cancel()

    #task = asyncio.create_task(periodic_sender(chat_id, hours))
    #user_data[chat_id] = {"interval_hours": hours, "task": task}
    await add_task(chat_id, send_time)

    await message.answer(
        f"Теперь каждый день в {hours}:00 ты будешь получать курс бакса/прогноза💰☁"
    )
    await state.clear()


async def main():
    dp.include_router(router)
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Off bot")
