import re
import random
import string


from database import *

import logging

logger = logging.getLogger(__name__)


def is_valid_username(username):
    # Проверяем, что имя пользователя состоит только из латинских букв
    pattern = r'^[a-zA-Z]+$'
    return bool(re.match(pattern, username))


def is_valid_email(email):
    """
    Проверяет, является ли переданная строка корректным email-адресом.
    :param email: Строка, содержащая email-адрес.
    :return: True, если email-адрес корректен, иначе False.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))


# Генерируем номер заказа
def generate_order_number():
    letters = string.ascii_uppercase
    digits = string.digits
    order_number = ''.join(random.choice(letters) + random.choice(digits) for _ in range(8))
    return order_number


def send_message(chat_id, message):
    from main import bot
    bot.send_message(chat_id=chat_id, text=message)


async def send_notifications():
    # Выбор записей из таблицы orders
    orders = get_orders_status_3()

    # Цикл по записям из таблицы orders
    for order in orders:
        order_id = order[0]
        user_id = order[1]

        # Выбор записей из таблицы order_items для данного order_id
        order_items = get_order_items(order_id)

        # Формирование сообщения
        message = f"""У вас сегодня запланирована доставка заказа. Состав заказа:
                {" ".join([f'{product_id} x{quantity}' for product_id, quantity in order_items])}"""

        # Отправка сообщения
        send_message(user_id, message)
