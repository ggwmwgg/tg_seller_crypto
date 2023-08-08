from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


upload = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Empty here"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)