import asyncio
import textwrap
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
load_dotenv()

from manager import Manager

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
manager = Manager()


class AddServiceFSM(StatesGroup):
    add_service_type = State()
    add_service = State()


class Supplier(StatesGroup):
    supplier = State()
    fast_sup = State()


async def start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Предоставить услугу", callback_data="become_supplier")
    builder.button(text="Записаться на услугу", callback_data="view_service_types")
    await message.answer("Вы желаете:", reply_markup=builder.as_markup())


@dp.message(Command("start"))
async def on_start(message: Message):
    first_time = manager.add_user(message.from_user.id, message.from_user.full_name)
    welcome_message = textwrap.dedent("""
           Привет! Это чат-бот по предоставлению и оказанию услуг* в общежитиях Металлург 1-3 Университета МИСИС.
           Здесь ты можешь найти необходимые тебе услуги поблизости и записаться на них. Приятного пользования!

           *-Создатели не осуществляют коммерческую деятельность. Команда создает ресурс для связи заказчика и клиента.
       """).strip()
    if first_time:
        print("he")
        await message.answer_photo(photo=FSInputFile("img.png"), caption=welcome_message)
    await start(message)


@dp.message(Command('add'))
async def add_menu(message: Message):
    if manager.get_user(message.from_user.id).role in ["admin"]:
        builder = InlineKeyboardBuilder()
        builder.button(text="Тип услуги", callback_data="add_service_type")
        builder.button(text="Услугу", callback_data="add_service")
        builder.adjust(1)
        await message.answer("Что вы хотите добавить:", reply_markup=builder.as_markup())


# service_type filter
@dp.callback_query(F.data == 'add_service_type')
async def add_service_type_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    builder = InlineKeyboardBuilder()
    builder.button(text="Будут услуги", callback_data="with_services_1")
    builder.button(text="Не будет услуг", callback_data="with_services_0")
    await callback.message.answer(text="Будут ли услуги?", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith('with_services_'))
async def with_services_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(with_service=int(callback.data.split('_')[-1]))

    await callback.message.answer("Оправьте иконку типа услуги и ее название.")
    await state.set_state(AddServiceFSM.add_service_type)


# add new service type
@dp.message(AddServiceFSM.add_service_type)
async def save_service_type(message: Message, state: FSMContext):
    title = message.caption
    photo_id = message.photo[-1].file_id
    path = f'images/{photo_id}.jpg'
    await message.bot.download(photo_id, path)
    manager.add_service_type(title, message.from_user.id, path, (await state.get_data())['with_service'])
    await message.answer("Тип услуги добавлен.")
    await state.clear()


# service filter
@dp.callback_query(F.data == "add_service")
async def add_service_start(callback: CallbackQuery, state: FSMContext):
    service_types = manager.get_user_service_types(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    for stype in service_types:
        if stype.is_with_services:
            builder.button(text=stype.title, callback_data=f"stype_{stype.id}")
    builder.adjust(1)
    await callback.answer()
    await state.set_state(AddServiceFSM.add_service)
    await callback.message.answer("Выберите тип услуги:", reply_markup=builder.as_markup())


# service_type_id filter
@dp.callback_query(F.data.startswith("stype_"), AddServiceFSM.add_service)
async def add_service_title(callback: CallbackQuery, state: FSMContext):
    stype_id = int(callback.data.split("_")[-1])
    await state.update_data(service_type_id=stype_id)
    await state.set_state(AddServiceFSM.add_service)
    await callback.answer()
    await callback.message.answer("Оправьте название услуги.")


# add new service
@dp.message(AddServiceFSM.add_service)
async def save_service(message: Message, state: FSMContext):
    data = await state.get_data()

    title = message.text
    manager.add_service(int(data['service_type_id']), title)
    await message.answer("Услуга добавлена.")
    await state.clear()


@dp.callback_query(F.data.startswith('service_type_'))
async def view_services(callback_query: CallbackQuery):
    service_type_id = int(callback_query.data.split('_')[2])
    sst = manager.get_service_type(service_type_id)
    builder = InlineKeyboardBuilder()
    services = manager.get_services(service_type_id)
    await callback_query.answer()
    if sst.is_with_services:
        if len(services) == 0:
            builder = InlineKeyboardBuilder()
            builder.button(text="Назад", callback_data='view_service_types')
            await callback_query.message.edit_text("Услуг не обнаружено.", reply_markup=builder.as_markup())
        else:
            for service in services:
                builder.button(text=service.title, callback_data=f'view_service_sup_{service.id}')
            builder.button(text="Назад", callback_data='view_service_types')
            builder.adjust(1)
            await callback_query.message.answer_photo(photo=FSInputFile(sst.image),
                                                      caption="Какую услугу вы хотите получить?",
                                                      reply_markup=builder.as_markup())
    else:
        msg = f"Cписок мастеров, предоставляющих {sst.title}:"
        for i in sst.suppliers:
            msg += f'\n{i}'

        await callback_query.message.answer_photo(caption=msg, photo=FSInputFile(sst.image))
        await callback_query.message.answer("Приятного пользования!\nДо скорой встречи!")


@dp.callback_query(F.data == "view_service_types")
async def back_to_service_types(callback_query: CallbackQuery):
    await callback_query.answer()
    service_types = manager.get_service_types()
    if len(service_types) == 0:
        await callback_query.message.edit_text("Услуг не обнаружено.")
    else:
        builder = InlineKeyboardBuilder()
        for service_type in service_types:
            builder.button(text=service_type.title, callback_data=f'service_type_{service_type.id}')
        builder.adjust(1)
        await callback_query.message.answer("Выберите тип услуги:", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "become_supplier")
async def become_supplier(callback_query: CallbackQuery):
    await callback_query.answer()
    service_types = manager.get_service_types()
    if len(service_types) == 0:
        await callback_query.message.edit_text("Услуг не обнаружено.")
    else:
        builder = InlineKeyboardBuilder()
        for service_type in service_types:
            builder.button(text=service_type.title, callback_data=f'st_sup_{service_type.id}')
        builder.adjust(1)
        await callback_query.message.edit_text("Выберите тип услуги для предоставления:",
                                               reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("st_sup_"))
async def cho(callback_query: CallbackQuery, state: FSMContext):
    service_type_id = int(callback_query.data.split('_')[-1])
    builder = InlineKeyboardBuilder()
    await state.set_state(Supplier.supplier)
    services = manager.get_services(service_type_id)
    sstype = manager.get_service_type(service_type_id)
    if sstype.is_with_services:
        if len(services) == 0:
            builder = InlineKeyboardBuilder()
            builder.button(text="Назад", callback_data='become_supplier')
            await callback_query.message.edit_text("Услуг не обнаружено.", reply_markup=builder.as_markup())
        else:
            for service in services:
                builder.button(text=service.title, callback_data=f'sup_{service.id}')
            builder.button(text="Назад", callback_data='become_supplier')
            builder.adjust(1)
            await callback_query.message.edit_text("Какую услугу вы желаете оказать?", reply_markup=builder.as_markup())
    else:
        await state.set_state(Supplier.fast_sup)
        await state.update_data(sssstype=service_type_id)
        await callback_query.message.answer(
            "Напишите Ваше имя телеграм-пользователя.\nНапример: @bob2012.\nУкажите дополнительную информацию через пробел, если потребуется.")


@dp.message(Supplier.fast_sup)
async def fast(message: Message, state: FSMContext):
    await message.answer("Вы внесены в список мастеров!\nДо скорой встречи!")
    manager.add_sup((await state.get_data())['sssstype'], message.text)
    await state.clear()


@dp.callback_query(F.data.startswith('sup_'))
async def view_srvices(callback_query: CallbackQuery, state: FSMContext):
    service_id = int(callback_query.data.split('_')[-1])
    await state.set_state(Supplier.supplier)
    await callback_query.answer()
    await state.update_data(ss_id=service_id)
    await callback_query.message.answer(
        "Напишите Ваше имя телеграм-пользователя.\nНапример: @bob2012.\nУкажите дополнительную информацию через пробел, если потребуется.")


@dp.message(Supplier.supplier)
async def view_servies(message: Message, state: FSMContext):
    await message.answer("Вы внесены в список мастеров!\nДо скорой встречи!")
    manager.add_supplier((await state.get_data())['ss_id'], message.text)
    await state.clear()


@dp.callback_query(F.data.startswith('view_service_sup_'))
async def view_services(callback_query: CallbackQuery):
    service_id = int(callback_query.data.split('_')[-1])
    lit = manager.get_service(service_id).suppliers
    await callback_query.answer()
    if len(lit) == 0:
        await callback_query.message.answer("Мастеров не найдено :(")
    else:
        msg = f"Cписок мастеров, предоставляющих {manager.get_service(service_id).title}:"
        for i in manager.get_service(service_id).suppliers:
            msg += f'\n{i}'

        await callback_query.message.answer(msg)
        await callback_query.message.answer("Приятного пользования!\nДо скорой встречи!")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
