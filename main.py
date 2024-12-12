import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers.__init__ import register_handlers


def initialize():
    load_dotenv()
    bot = Bot(token=os.getenv('API_TOKEN'))
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers(dp)

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    initialize()
