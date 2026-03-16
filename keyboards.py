from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def main_kkb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Запросить курс/прогноз сейчас', style='success')],
            [KeyboardButton(text='Отменить рассылку', style='danger')]
        ],
        resize_keyboard = True,
        #input_field_placeholder='Выбери чифру или напиши свою...'
    )

    return keyboard

def select_number():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='⏰ 1h', callback_data='1')],
            [InlineKeyboardButton(text='⏰ 6h', callback_data='6')],
            [InlineKeyboardButton(text='⏰ 12h', callback_data='12')],
            [InlineKeyboardButton(text='⏰ 18h', callback_data='18')],
            [InlineKeyboardButton(text='⏰ 24h', callback_data='24')],
        ]
    )
    return keyboard
