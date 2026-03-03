from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def main_kkb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Запросить курс/прогноз сейчас', style='primary')],
        ],
        resize_keyboard = True,
        #input_field_placeholder='Выбери чифру или напиши свою...'
    )

    return keyboard