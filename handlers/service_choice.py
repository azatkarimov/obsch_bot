from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.keyboards import create_keyboard
from utils.states import States


async def handle_service_choice(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    extra_param = callback_data['extra_param']
    with open('images/uslugi.jpg', 'rb') as photo_file:
        labels = {
            '💅 Красота': 'beauty_service',
            '📚 Учеба': 'study_service',
            '🏠 Быт': 'other_service',
            '◀️ Назад': 'back_to_start'
        }
        keyboard = create_keyboard(
            labels=labels,
            extra_param=extra_param
        )

        await query.message.edit_media(
            media=types.InputMediaPhoto(photo_file, "Выбор типа услуги"),
            reply_markup=keyboard
        )

        await state.set_state(States.STOP_INPUT)