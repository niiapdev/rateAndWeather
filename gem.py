import asyncio
import logging
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import time, datetime
from zoneinfo import ZoneInfo

# Твои настройки и парсеры
from config import TG_API_BOT
from main import get_rate
from weather import get_weather
from keyboards import main_kkb, select_number

# Импортируем функции из твоего нового файла db.py
from db2 import add_task, get_active_tasks, deactivate_task, init_db

router = Router()
dp = Dispatcher()
bot = Bot(token=TG_API_BOT)

task_input = 'В какое время дня отправлять тебе обновленную инфу?⏰\n\nНажми на кнопку или↔️\nВведи число (например: 24):'


class SetInterval(StatesGroup):
    waiting_for_hours = State()


# --- ФОНОВАЯ ЗАДАЧА (SCHEDULER) ---
async def scheduler():
    while True:
        # Устанавливаем московское время
        now = datetime.now(ZoneInfo('Europe/Moscow'))
        # Обнуляем секунды, чтобы сравнение сработало ровно в 00 секунд
        current_time = now.time().replace(second=0, microsecond=0)

        # Получаем список активных задач из SQLite
        tasks = await get_active_tasks()

        for task in tasks:
            # В SQLite мы сохранили время, и db.py отдает его как объект time
            if task['send_time'] == current_time:
                chat_id = task['chat_id']
                weather = get_weather()
                rate = get_rate()

                try:
                    await bot.send_message(
                        chat_id,
                        f"💵 Доллар: {rate['usd']} RUB\n"
                        f"💴 Йены: 0.{rate['jpy']} RUB\n"
                        f"🌡 Температура сейчас: {weather['current']}℃"
                    )
                except Exception as e:
                    logging.error(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}")

        # Спим 50 секунд, чтобы не пропускать минуты и не нагружать процессор
        await asyncio.sleep(50)


# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ОТПРАВКИ ---
async def send_rate_weather(message: Message):
    weather = get_weather()
    rate = get_rate()
    await message.answer(
        f"💲 Курс доллара: {rate['usd']} RUB\n"
        f"💴 Курс йены: 0.{rate['jpy']} RUB\n\n"
        f"⛅ Прогноз Ростова-на-Дону на сегодня:\n"
        f"🌡 Сейчас: {weather['current']}℃\n"
        f"⬆ Макс: {weather['max']}℃\n"
        f"⬇ Мин: {weather['min']}℃",
        reply_markup=main_kkb()
    )


# --- ХЕНДЛЕРЫ (ОБРАБОТЧИКИ КОМАНД) ---

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await send_rate_weather(message)
    await message.answer(task_input, reply_markup=select_number())
    await state.set_state(SetInterval.waiting_for_hours)


@router.message(F.text == 'Запросить курс/прогноз сейчас')
async def cmd_wr(message: Message, state: FSMContext):
    await send_rate_weather(message)
    await message.answer(task_input, reply_markup=select_number())
    await state.set_state(SetInterval.waiting_for_hours)


@router.message(F.text == 'Отменить рассылку')
async def cmd_clear(message: Message):
    chat_id = message.chat.id
    # Вызываем функцию деактивации. Она вернет количество измененных строк.
    rows_affected = await deactivate_task(chat_id)

    if rows_affected == 0:
        await message.answer('Активной рассылки у вас нет!❌')
    else:
        await message.answer('Рассылка была успешно отменена🛑')


@router.callback_query(SetInterval.waiting_for_hours, F.data.isdigit())
async def hours_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

    hours = int(callback.data)
    chat_id = callback.message.chat.id
    send_time = time(hours, 0)

    # Сохраняем задачу в нашу SQLite базу
    await add_task(chat_id, send_time)

    await callback.message.answer(
        f"Теперь каждый день в {hours}:00 ты будешь получать курс бакса/прогноза💰☁"
    )
    await state.clear()


@router.message(SetInterval.waiting_for_hours, F.text)
async def process_hours(message: Message, state: FSMContext):
    try:
        hours = int(message.text)
        if not (0 <= hours <= 23):  # Проверка на корректность часа
            raise ValueError
    except ValueError:
        await message.answer("Введите число от 0 до 23! 🤬")
        return

    chat_id = message.chat.id
    send_time = time(hours, 0)

    # Сохраняем задачу в нашу SQLite базу
    await add_task(chat_id, send_time)

    await message.answer(
        f"Теперь каждый день в {hours}:00 ты будешь получать курс бакса/прогноза💰☁"
    )
    await state.clear()


# --- ЗАПУСК БОТА ---
async def main():
    # 1. Сначала инициализируем базу (создаем таблицу, если её нет)
    await init_db()

    # 2. Регистрируем роутеры
    dp.include_router(router)

    # 3. Запускаем фоновый планировщик
    asyncio.create_task(scheduler())

    # 4. Начинаем слушать сообщения
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
