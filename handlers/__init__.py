from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

from handlers.callback import button_callback
from handlers.option import handle_option
from handlers.other_service import handle_other_service, handle_provide_other, handle_sign_up_other
from handlers.start import start, handle_back_to_start
from handlers.service_choice import handle_service_choice
from handlers.beauty_service import handle_beauty_service
from handlers.study_service import handle_study_service
from utils.states import States

command_handlers = [
    (start, 'start')
]

message_handlers = [

]

# Список обработчиков callback_query
callback_query_handlers = [
    (handle_service_choice, ['service_choice', 'back_to_choice']),
    (handle_back_to_start, ['back_to_start']),

    (handle_beauty_service, ['beauty_service']),
    (handle_study_service, ['study_service']),
    (handle_other_service, ['other_service']),
    (handle_sign_up_other, ['sign_up_other']),

    (handle_option, ['manicure', 'pedicure', 'makeup', 'economic', 'english', 'math', 'presentations', 'other']),
]

# Список обработчиков состояния
state_handlers = [
    (handle_provide_other, States.WAITING_FOR_INPUT)
]


def register_handlers(dp: Dispatcher):
    for handler, command in command_handlers:
        dp.register_message_handler(handler, commands=command, state='*')

    for handler, message in message_handlers:
        dp.register_message_handler(handler, Text(endswith=message), state='*')


    for handler, actions in callback_query_handlers:
        for action in actions:
            dp.register_callback_query_handler(handler, button_callback.filter(action=action), state='*')

    for handler, state in state_handlers:
        dp.register_message_handler(handler, state=state)
