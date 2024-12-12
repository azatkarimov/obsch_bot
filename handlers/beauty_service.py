from aiogram import types
from utils.keyboards import create_keyboard


async def handle_beauty_service(query: types.CallbackQuery, callback_data: dict):
    extra_param = callback_data['extra_param']
    with open('images/beauty.jpg', 'rb') as photo_file:
        labels = {
            'Маникюр': 'manicure',
            'Педикюр': 'pedicure',
            'Макияж и брови': 'makeup',
            '◀️ Назад': 'back_to_choice',
            '⏪ В начало': 'back_to_start'
        }
        keyboard = create_keyboard(labels, extra_param)

        await query.message.edit_media(
            media=types.InputMediaPhoto(photo_file, "Выбор услуги"),
            reply_markup=keyboard
        )
