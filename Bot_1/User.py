
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


import logging

from database import *
from keyboards import *
from utils import *


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


async def start(message: types.Message):
    await message.answer('Привет! Я бот, помогающий заказать доставку.', reply_markup=kb_start)


async def info(message: types.Message):
    info_text = "Бот позволяет заказать доставку, а также получить информацию " \
                "о ранее сделанных доставках"

    await message.answer(info_text)


async def new_order_request(message: types.Message):
    # Получаем список продуктов из базы данных
    products = get_all_products()

    for product in products:
        # Выводим информацию по продукту
        await message.answer(f"Вы можете заказать доставку: "
                             f"<b>{product[1]}</b> по цене: {product[2]} руб.")
    # Отправляем сообщение с клавиатурой
    await message.answer('Выберите продукт для покупки', reply_markup=get_kb_products(products))


async def send_confirm_message(call: types.CallbackQuery):
    # Получаем информацию о продукте из базы данных
    product_id = int(call.data.split('_')[-1])
    product_info = get_product_by_id(product_id)

    if product_info:
        product_name, product_price = product_info
        await call.message.answer(f"Вы добавили : {product_name} в корзину")
    else:
        await call.message.answer('Произошла ошибка при получении информации о продукте.')
    await call.answer()


async def profile(message: types.Message):
    await message.answer("просмтреть профиль")


async def sign_up(message: types.Message):
    await message.answer("Для начала регистрации введите имя пользователя",
                         reply_markup=get_kb_cancel("только латинский алфавит"))
    await RegistrationState.username.set()


async def cancel_registration(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Регистрация отменена.")
    await call.answer()


async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    if is_included(username):
        await message.answer("Пользователь существует, введите другое имя")
        return
    if not is_valid_username(username):
        await message.answer("Неверное имя пользователя, введите другое имя")
        return

    async with state.proxy() as data:
        data['username'] = username
        await message.answer("Введите свой email:", reply_markup=get_kb_cancel("адрес вида user@example.com"))
        await RegistrationState.email.set()


async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    if not is_valid_email(email):
        await message.answer("Неверный email, введите другой")
        return
    async with state.proxy() as data:
        data['email'] = email
    await message.answer("Введите свой возраст:", reply_markup=get_kb_cancel("возраст > 0 и < 120"))
    await RegistrationState.age.set()


async def set_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        return
    if age <= 0 or age > 120:
        await message.answer("Неверный возраст, введите > 0 и < 120.")
        return

    async with state.proxy() as data:
        data['age'] = age
    add_user(data['username'], data['email'], data['age'])
    await message.answer("Регистрация успешно завершена!")
    await state.finish()


async def global_error_handler(update: types.Update, exception: Exception):
    logging.exception(exception)
    await update.message.reply("Извините, произошла ошибка. Пожалуйста, попробуйте позже.")
    return True


#   Обрабатывает сообщения, которые не были распознаны другими обработчиками
async def unknown_message(message: types.Message):
    logging.info(f'Получено неизвестное сообщение от {message.from_user.username}: {message.text}')
    await message.answer('Извините, я не понимаю это сообщение. Пожалуйста, попробуйте что-нибудь другое.')
