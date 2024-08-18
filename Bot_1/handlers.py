import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests

from database import *
from keyboards import *


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


async def start(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=kb_start)


async def cancel_registration(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Регистрация отменена.")
    await call.answer()
# if call.message.reply_markup is not None:
#    await call.message.edit_reply_markup(reply_markup=None)


async def sing_up(message: types.Message):
    await message.answer("Для начала регистрации введите имя пользователя (только латинский алфавит)", reply_markup=kb_cancel)
    await RegistrationState.username.set()


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
        await message.answer("Введите свой email:", reply_markup=kb_cancel)
        await RegistrationState.email.set()


async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    if not is_valid_email(email):
        await message.answer("Неверный email, введите другой")
        return
    async with state.proxy() as data:
        data['email'] = email
    await message.answer("Введите свой возраст:", reply_markup=kb_cancel)
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


async def get_buying_list(message: types.Message):
    # Получаем список продуктов из базы данных
    products = get_all_products()

    for product in products:
        # Выводим информацию по продукту
        await message.answer(f"Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}")
        product_photo = product[4]
        # Проверяем, существует ли фотография
        if product_photo:
            try:
                # Проверяем, можно ли загрузить фото по URL-адресу
                response = requests.get(product_photo)
                if response.status_code == 200:
                    # Отправляем изображение
                    await message.answer_photo(photo=product_photo)
                else:
                    await message.answer(f"Фото продукта отсутствует 1")
            except requests.exceptions.RequestException:
                await message.answer(f"Фото продукта отсутствует 2")
        else:
            await message.answer(f"Фото продукта отсутствует")

    # Отправляем сообщение с клавиатурой
    await message.answer('Выберите продукт для покупки', reply_markup=get_kb_products(products))


async def send_confirm_message(call: types.CallbackQuery):
    # Получаем информацию о продукте из базы данных
    product_id = int(call.data.split('_')[-1])
    product_info = get_product_by_id(product_id)

    if product_info:
        product_name, product_price = product_info
        await call.message.answer(f'Вы успешно приобрели продукт: {product_name} за {product_price} руб.')
    else:
        await call.message.answer('Произошла ошибка при получении информации о продукте.')
    await call.answer()


async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=kb_calc)


async def get_formulas(call: types.CallbackQuery):
    formula = "Формула Миффлина-Сан Жеора:\n"
    formula += "Для мужчин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5"
    await call.message.answer(formula)
    await call.answer()


async def get_calories(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


async def set_user_age(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


async def set_user_growth(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


async def set_user_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()

    # Вычисление нормы калорий по упрощенной формуле Миффлина-Сан Жеора для мужчин
    if data['growth'] > 0 and data['weight'] > 0 and data['age'] > 0:
        calories = 10 * data['weight'] + 6.25 * data['growth'] - 5 * data['age'] + 5
        await message.answer(f'Ваша норма калорий: {int(calories)} ккал/день')
    else:
        await message.answer('Не удалось рассчитать норму калорий. Проверьте введенные данные.')

    await state.finish()


async def show_info(message: types.Message):
    info_text = "Бот позволяет рассчитать вашу суточную норму калорий " \
                "по упрощенной формуле Миффлина-Сан Жеора для мужчин. Для этого вам нужно " \
                "ввести ваш возраст, рост и вес." \
                "\n<b>Также Вы можете приобрести сопутствующие товары.</b>"
    await message.answer(info_text)


async def global_error_handler(update: types.Update, exception: Exception):
    logging.exception(exception)
    await update.message.reply("Извините, произошла ошибка. Пожалуйста, попробуйте позже.")
    return True


#   Обрабатывает сообщения, которые не были распознаны другими обработчиками
async def unknown_message(message: types.Message):
    logging.info(f'Получено неизвестное сообщение от {message.from_user.username}: {message.text}')
    await message.answer('Извините, я не понимаю это сообщение. Пожалуйста, попробуйте что-нибудь другое.')
