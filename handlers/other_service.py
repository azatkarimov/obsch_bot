from aiogram import types
from aiogram.dispatcher import FSMContext
import datetime as dt

from handlers import button_callback
from utils.states import States
from utils.users import users_data, update_users_data


async def handle_other_service(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    extra_param = callback_data['extra_param']
    username = str(query.from_user.username)
    if username in users_data:
        user_data = users_data[username]
    else:
        user_data = users_data[username] = {}
    with open('images/other.jpg', 'rb') as photo_file:
        keyboard = types.InlineKeyboardMarkup()
        if extra_param == 'provide':
            caption = ('Введите услугу, которую хотите добавить' +
                        (' или удалить\n\nСписок предоставляемых услуг:\n' +
                         '\n'.join(['• ' + option for option in user_data['other']])
                        if 'other' in user_data and user_data['other'] else ''))
            await state.set_state(States.WAITING_FOR_INPUT)
        else:
            caption = ('Выбор услуги' if any(True for user_data in users_data.values()
                        if 'other' in user_data and user_data['other']) else
                       'Никто не предоставляет услуги в категории «Быт»')
            labels = []
            for user_data in users_data.values():
                if 'other' in user_data:
                    labels.extend(user_data['other'])
            buttons = [
                types.InlineKeyboardButton(
                    text=label,
                    callback_data=button_callback.new(
                        action='sign_up_other',
                        extra_param=label
                    )
                ) for label in labels
            ]
            for i in range(0, len(buttons), 2):
                keyboard.add(*buttons[i:i + 2])

        labels_actions = {'◀️ Назад': 'back_to_choice', '⏪ В начало': 'back_to_start'}
        buttons = [
            types.InlineKeyboardButton(
                text=label,
                callback_data=button_callback.new(
                    action=action,
                    extra_param=extra_param
                )
            ) for label, action in labels_actions.items()
        ]
        keyboard.add(*buttons)

        await query.message.edit_media(
            media=types.InputMediaPhoto(photo_file, caption), reply_markup=keyboard
        )


async def handle_provide_other(message: types.Message, state: FSMContext, option_name=None, username=None):
    if not option_name:
        option_name = message.text.strip()
    if not username:
        username = str(message.from_user.username)
    user_data = users_data[username]
    if 'other' in user_data:
        service_data = user_data['other']
        if option_name in service_data:
            service_data.remove(option_name)
        else:
            service_data.append(option_name)
    else:
        user_data['other'] = []
        user_data['other'].append(option_name)
    update_users_data(users_data)

    text = f'Теперь вы предоставляете услугу «{option_name}»' if option_name in user_data['other'] \
        else f'Вы больше не предоставляете услугу «{option_name}»'
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
            text='⏪ В начало',
            callback_data=button_callback.new(
                action='back_to_start',
                extra_param=''
            )
        )
    )

    user_data['last_update'] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(States.STOP_INPUT)


async def handle_sign_up_other(query: types.CallbackQuery, callback_data: dict):
    option_name = callback_data['extra_param']
    active_users = [username for username, user_data in users_data.items()
                    if 'other' in user_data and option_name in user_data['other']]
    caption = f'Пользователи предоставляющие услугу «{option_name}»' \
        if active_users else f'Никто не предоставляет услугу «{option_name}»'
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(
            text='@' + user,
            url=f'https://t.me/{user}'  # URL передается напрямую, а не через callback_data
        )
        for user in active_users
    ]
    for i in range(0, len(buttons), 2):
        keyboard.add(*buttons[i:i + 2])
    keyboard.add(types.InlineKeyboardButton(
            text='⏪ В начало',
            callback_data=button_callback.new(
                action='back_to_start',
                extra_param=''
            )
        )
    )

    with open(f'images/other.jpg', 'rb') as photo_file:
        await query.message.edit_media(
            media=types.InputMediaPhoto(photo_file, caption),
            reply_markup=keyboard
        )
