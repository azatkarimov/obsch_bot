from aiogram import types

from handlers import button_callback
from utils.users import users_data, update_users_data
import datetime as dt


async def handle_option(query: types.CallbackQuery, callback_data: dict):
    action = callback_data['action']
    actions = {'manicure': 'Маникюр',
               'pedicure': 'Педикюр',
               'makeup': 'Макияж и брови',
               'economic': 'Помощь с экономикой',
               'english': 'Помощь с английским',
               'math': 'Помощь с математикой',
               'presentations': 'Презентации'}
    option_name = actions[action]
    services = [('beauty', ['manicure', 'pedicure', 'makeup']),
                ('study', ['economic', 'english', 'math', 'presentations'])]
    service_name = [key for key, value in services if action in value][0]
    extra_param = callback_data['extra_param']
    if extra_param == 'provide':
        username = str(query.from_user.username)
        if username in users_data:
            user_data = users_data[username]
        else:
            user_data = users_data[username] = {}
        if service_name in user_data:
            service_data = user_data[service_name]
            if action in service_data:
                service_data[action] = not service_data[action]
            else:
                service_data[action] = True
        else:
            user_data[service_name] = {}
            user_data[service_name][action] = True
        update_users_data(users_data)

        if user_data[service_name][action]:
            await query.answer(f'Теперь вы предоставляете услугу «{option_name}»')
        else:
            await query.answer(f'Вы больше не предоставляете услугу «{option_name}»')

        user_data['last_update'] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        active_users = [username for username in users_data.keys()
                        if service_name in users_data[username]
                        and action in users_data[username][service_name]
                        and users_data[username][service_name][action]]
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

        with open(f'images/{service_name}.jpg', 'rb') as photo_file:
            await query.message.edit_media(
                media=types.InputMediaPhoto(photo_file, caption),
                reply_markup=keyboard
            )
