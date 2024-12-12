from aiogram import types
from handlers import button_callback


def create_keyboard(labels: dict, extra_param):
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(
            text=key,
            callback_data=button_callback.new(
                action=value,
                extra_param=extra_param
            )
        ) for key, value in labels.items()
    ]
    length = len(buttons)
    fl = length < 6
    if fl:
        keyboard.add(buttons[0])
    for i in range(int(fl), length, 2):
        keyboard.add(*buttons[i:i + 2])

    return keyboard
