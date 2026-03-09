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