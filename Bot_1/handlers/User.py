import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime, timedelta

from database import *
from keyboards import *
from utils import *

logger = logging.getLogger(__name__)


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    phone = State()
    sity = State()
    address = State()


class Cart:
    def __init__(self):
        self.products = {}

    def add_product(self, product_name, price, quantity=1):
        if product_name not in self.products:
            self.products[product_name] = {'price': price, 'quantity': quantity}
        else:
            self.products[product_name]['quantity'] += quantity

    def remove_product(self, product_name):
        if product_name in self.products:
            del self.products[product_name]

    def update_quantity(self, product_name, quantity):
        if product_name in self.products:
            self.products[product_name]['quantity'] = quantity

    def get_quantity(self, product_name):
        return self.products.get(product_name, {}).get('quantity', 0)

    def get_price(self, product_name):
        return self.products.get(product_name, {}).get('price', 0)

    def get_total_price(self):
        return sum(product['price'] * product['quantity'] for product in self.products.values())

    def get_products(self):
        return self.products

    def is_empty(self):
        return len(self.products) == 0

    def clear(self):
        self.products = {}


async def start(message: types.Message):
    await message.answer('Привет! Я бот, помогающий заказать доставку.', reply_markup=kb_start)


async def info(message: types.Message):
    info_text = "Бот позволяет заказать доставку, а также получить информацию " \
                "о ранее сделанных доставках"

    await message.answer(info_text)


async def new_order_request(message: types.Message):
    logger.info = f"Начало заказа пользователя {message.from_user.username} id: {message.from_user.id}"

    # Получаем список городов из базы данных
    cities = get_cities()

    # Создаем inline клавиатуру для выбора города
    city_keyboard = types.InlineKeyboardMarkup()
    city_buttons = []
    for city in cities:
        city_buttons.append(types.InlineKeyboardButton(text=city[1], callback_data=f"city_{city[0]}"))
    city_keyboard.add(*city_buttons)

    # Предлагаем выбрать город для доставки заказа
    await message.answer("Выберите город для доставки заказа:", reply_markup=city_keyboard)


async def city_selected(call: types.CallbackQuery):
    city_id = int(call.data.split("_")[1])
    # Выводим информацию по продукту
    products = get_all_products(city_id)
    for product in products:
        await call.message.answer(f"Вы можете заказать доставку: "
                                 f"<b>{product[1]}</b> по цене: {product[4]} руб.")
    # Отправляем сообщение с клавиатурой
    await call.message.answer('Выберите продукт для покупки', reply_markup=get_kb_products(products))

    # Храним список products в глобальной переменной
    global products_list
    products_list = products

async def send_confirm_message(call: types.CallbackQuery):
    product_id = int(call.data.split('_')[-1])
    product_info = next((product for product in products_list if product[0] == product_id), None)
    global cart
    cart=Cart()
    if product_info:
        product_name, product_price = product_info[1], product_info[4]

        # Проверяем, есть ли продукт в корзине
        if cart.get_quantity(product_name) > 0:
            # Если продукт уже есть в корзине, предлагаем увеличить количество
            await call.message.answer(f"Вы уже добавили {product_name} в корзину. Хотите увеличить количество?")
            # Добавляем кнопки для увеличения/уменьшения количества
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("Увеличить", callback_data=f"inc_{product_name}"))
            keyboard.add(types.InlineKeyboardButton("Уменьшить", callback_data=f"dec_{product_name}"))
            await call.message.answer("Выберите действие:", reply_markup=keyboard)
        else:
            # Если продукта нет в корзине, добавляем его
            await call.message.answer(f"Вы добавили {product_name} в корзину. Цена: {product_price}")
            await call.message.answer("Введите количество (по умолчанию - 1):")
            quantity = await call.message.answer()
            if quantity.text:
                try:
                    quantity = int(quantity.text)
                    if quantity <= 0:
                        await call.message.answer("Количество должно быть положительным числом.")
                        return
                except ValueError:
                    await call.message.answer("Некорректное количество. Использую значение по умолчанию - 1.")
                    quantity = 1
            else:
                quantity = 1
            cart.add_product(product_name, product_price, quantity)
            await call.message.answer(f"Вы добавили {quantity} x {product_name} в корзину.")
            # Запрашиваем пользователя продолжить или перейти к оформлению заказа
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("Продолжить", callback_data="continue"))
            keyboard.add(types.InlineKeyboardButton("Оформить заказ", callback_data="checkout"))
            await call.message.answer("Что дальше?", reply_markup=keyboard)
    else:
        await call.message.answer('Произошла ошибка при получении информации о продукте.')
        logger.error(f'Произошла ошибка при получении информации о продукте {product_id}, {product_info}')
    await call.answer()


class OrderForm(StatesGroup):
    delivery_date = State()
    delivery_time = State()
    confirm = State()


async def start_order(call: types.CallbackQuery):
    await call.message.answer("Введите адрес доставки:")
    await OrderForm.delivery_date.set()


async def select_delivery_date(message: types.Message, state: FSMContext):
    # Получаем текущую дату
    today = datetime.now().date()

    # Создаем объект календаря
    calendar = types.InlineKeyboardMarkup()
    calendar.add(types.InlineKeyboardButton(today.strftime("%d.%m.%Y"), callback_data=f"date_{today.strftime('%Y-%m-%d')}"))

    # Добавляем кнопки для следующих дней
    for i in range(1, 7):
        date = today + timedelta(days=i)
        calendar.add(types.InlineKeyboardButton(date.strftime("%d.%m.%Y"), callback_data=f"date_{date.strftime('%Y-%m-%d')}"))

    # Отправляем сообщение с календарем
    await message.answer("Выберите дату доставки:", reply_markup=calendar)
    await state.update_data(delivery_date=message.text)

async def handle_delivery_date(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith("date_"):
        delivery_date = datetime.strptime(call.data.split("_")[1], "%Y-%m-%d").date()
        await state.update_data(delivery_date=delivery_date)
        await call.message.answer(f"Вы выбрали дату доставки: {delivery_date.strftime('%d.%m.%Y')}")
        await select_delivery_time(call, state)


async def select_delivery_time(call: types.CallbackQuery, state: FSMContext):
    # Создаем объект календаря
    calendar = types.InlineKeyboardMarkup()

    # Добавляем кнопки для выбора времени
    for hour in range(11, 17):
        for minute in [0, 30]:
            time = f"{hour}:{minute:02d}"
            calendar.add(types.InlineKeyboardButton(time, callback_data=f"time_{time}"))

    # Отправляем сообщение с календарем
    await call.message.answer("Выберите время доставки:", reply_markup=calendar)


async def handle_delivery_time(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith("time_"):
        delivery_time = call.data.split("_")[1]
        await state.update_data(delivery_time=delivery_time)
        await call.message.answer(f"Вы выбрали время доставки: {delivery_time}")
        await confirm_order(call, state)


async def confirm_order(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.answer(f"Ваш заказ:\nДата доставки: {data['delivery_date'].strftime('%d.%m.%Y')}\nВремя доставки: {data['delivery_time']}\nАдрес доставки: {data['delivery_address']}\n\nПодтвердите заказ:", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Подтвердить", callback_data="confirm")))


async def handle_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "confirm":
        data = await state.get_data()
        user_id = call.from_user.id
        delivery_date = data['delivery_date']
        delivery_time = data['delivery_time']
        delivery_address = data['delivery_address']
        cart = data['cart']

        # Генерируем номер заказа
        order_number = generate_order_number()

        # Записываем заказ в таблицу заказов
        order_id = await insert_order(user_id, delivery_date, delivery_time, delivery_address, order_number)

        # Записываем данные корзины в таблицу заказов
        for item in cart:
            await insert_order_item(order_id, item['product_id'], item['quantity'], item['price'])

        await call.message.answer(f"Ваш номер заказа: {order_number}")
        await state.reset_state()


async def view_orders(message: types.Message):
    user_id = message.from_user.id
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Новые", callback_data="orders_1"),
        types.InlineKeyboardButton(text="В обработке", callback_data="orders_2"),
        types.InlineKeyboardButton(text="В доставке", callback_data="orders_3"),
        types.InlineKeyboardButton(text="Выполненные", callback_data="orders_4"),
        types.InlineKeyboardButton(text="Все", callback_data="orders_all")
    ]
    keyboard.add(*buttons)
    await message.answer("Выберите статус заказов:", reply_markup=keyboard)


async def orders_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    if call.data == "orders_1":
        orders = get_orders_by_status(user_id, 1)
    elif call.data == "orders_2":
        orders = get_orders_by_status(user_id, 2)
    elif call.data == "orders_3":
        orders = get_orders_by_status(user_id, 3)
    elif call.data == "orders_4":
        orders = get_orders_by_status(user_id, 4)
    elif call.data == "orders_all":
        orders = get_orders(user_id)
    for order in orders:
        await call.message.answer(f"Заказ #{order[0]}: {order[1]}")

async def profile(message: types.Message):
    await message.answer("просмотреть профиль")


async def sign_up(message: types.Message):
    await message.answer("Для начала регистрации введите имя получателя заказов",
                         reply_markup=get_kb_cancel("прервать регистрацию"))
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
        add_user(data)
#        User.to_db()

        await message.answer("Ваше имя: " + data['username'] + "\n"
                             "Ваш email: " + data['email'] + "\n"
                             "Ваш возраст: " + str(data['age']) + "\n")
        add_user(data)
        await message.answer("Спасибо за регистрацию!", reply_markup=kb_start)
        await state.finish()


async def global_error_handler(update: types.Update, exception: Exception):
    logging.exception(exception)
    await update.message.reply("Извините, произошла ошибка. Пожалуйста, попробуйте позже.")
    return True


#   Обрабатывает сообщения, которые не были распознаны другими обработчиками
async def unknown_message(message: types.Message):
    logging.info(f'Получено неизвестное сообщение от {message.from_user.username}: {message.text}')
    await message.answer('Извините, я не понимаю это сообщение. Пожалуйста, попробуйте что-нибудь другое.')
