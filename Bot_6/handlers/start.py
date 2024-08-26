import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import add_user, get_user
from utils import is_valid_email, is_admin
from datetime import datetime
from keyboards.main import main_menu

logger = logging.getLogger(__name__)


async def start(message: types.Message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if user:
        if user[4]:  # if user is banned
            await message.answer("Вы заблокированы. Напишите администратору для разблокировки.", reply_markup=None)
        else:
            await message.answer(f"Добро пожаловать, {user[1]}!")
            await message.answer("Выберите действие:", reply_markup=main_menu(is_admin(user_id)))
    else:
        await message.answer(
            "Получать напоминания могут только зарегистрированные пользователи. Пожалуйста, зарегистрируйтесь")
        await register_user(message)


class RegistrationState(StatesGroup):
    name = State()
    email = State()


async def register_user(message: types.Message):
    await message.answer("Пожалуйста, введите ваше имя:")
    await RegistrationState.name.set()


async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        await message.answer("Пожалуйста, введите ваш email:")
        await RegistrationState.email.set()


async def process_email(message: types.Message, state: FSMContext):
    email = message.text
    if not is_valid_email(email):
        await message.answer("Неверный email, введите другой")
        return
    async with state.proxy() as data:
        data['email'] = email
        user_id = message.from_user.id
        name = data['name']
        registration_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        await add_user(user_id, name, data['email'], registration_date)
        await message.answer("Вы успешно зарегистрированы!")
        await state.finish()
#        await show_main_menu(message)


async def show_main_menu(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu)


async def global_error_handler(update: types.Update, exception: Exception):
    logger.exception(exception)
    if update.message:
        await update.message.reply("Извините, произошла ошибка. Пожалуйста, попробуйте позже.")
    else:
        logging.error("Error occurred: %s", exception)


#   Обрабатывает сообщения, которые не были распознаны другими обработчиками
async def unknown_message(message: types.Message):
    logger.info(f'Получено неизвестное сообщение от {message.from_user.username}: {message.text}')
    await message.answer('Извините, я не понимаю это сообщение. Пожалуйста, попробуйте что-нибудь другое.')


async def info(message: types.Message):
    await message.answer(f"<b>Это бот для работы с напоминаниями</b>.\nДля создания и получения напоминаний необходимо пройти регистрацию.")

