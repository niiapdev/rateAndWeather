from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def main_kkb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Запросить курс/прогноз сейчас', style='success')],
        ],
        resize_keyboard = True,
        #input_field_placeholder='Выбери чифру или напиши свою...'
    )

    return keyboard

def select_number():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='1', callback_data='1')],
            [InlineKeyboardButton(text='6', callback_data='6')],
            [InlineKeyboardButton(text='12', callback_data='12')],
            [InlineKeyboardButton(text='18', callback_data='18')],
            [InlineKeyboardButton(text='24', callback_data='24')],
        ]
    )
    return keyboard