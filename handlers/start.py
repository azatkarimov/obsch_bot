from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers import button_callback
from utils.states import States


async def start(message: types.Message, state: FSMContext, is_back=False):
    """Обработчик команды /start."""
    caption = ('Привет! Это чат-бот по предоставлению и оказыванию*'
               ' услуг в общежитиях Металлург 1-3 Университета МИСИС.'
               ' Здесь ты можешь найти необходимые тебе услуги поблизости '
               'и записаться на них. Приятного пользования!\n\n'
               '*— Создатели не осуществляют коммерческую деятельность.'
               ' Команда создает ресурс для связи заказчика и клиента.')
    labels = [
        'Предоставить услугу',
        'Записаться на услугу'
    ]
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(
            text=label,
            callback_data=button_callback.new(
                action='service_choice',
                extra_param='provide' if label == 'Предоставить услугу' else 'sign_up'
            )
        ) for label in labels
    ]
    keyboard.add(*buttons)

    with open('images/uslugi.jpg', 'rb') as photo_file:
        caption = caption
        if is_back:
            await message.edit_media(
                media=types.InputMediaPhoto(photo_file, caption),
                reply_markup=keyboard
            )
        else:
            await message.answer_photo(photo_file, caption=caption, reply_markup=keyboard)

    await state.set_state(States.STOP_INPUT)


async def handle_back_to_start(query: types.CallbackQuery, state: FSMContext):
    await start(query.message, state=state, is_back=True)