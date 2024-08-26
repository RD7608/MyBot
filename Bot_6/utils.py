import asyncio
import logging
import re
from datetime import datetime, date

from config import bot,ADMINS
from database import get_user, get_reminders_by_time, set_reminder_status

logger = logging.getLogger(__name__)


async def send_reminders():
    # получи напоминания на текущую дату и время
    c_date = date.today()
    c_time = datetime.now().strftime('%H:%M')
    reminders = await get_reminders_by_time(c_date, c_time)
    if reminders:
        for reminder in reminders:
            # отправить напоминание
            if await send_message(reminder):
                await set_reminder_status(reminder[0], reminder[1], 1)
                await asyncio.sleep(1)  # задержка в 1 секунду
            else:
                await set_reminder_status(reminder[0], reminder[1], 3)


async def send_message(reminder):
    user_id = reminder[1]
    event_type = reminder[2]
    event_name = reminder[3]
    event_message = reminder[4]
    event_date = reminder[5]
    event_time = reminder[6]
    message = f"⏰ {event_type} {event_name}\n : {event_message}"
    await bot.send_message(chat_id=user_id, text=message)
    logger.info(f"Отправлено {reminder}")
    return True


def is_admin(user_id):
    return user_id in ADMINS


async def is_banned(user_id):
    user = await get_user(user_id)
    if user[4] == 1:
        return True
    else:
        return False


def is_valid_email(email):
    """
    Проверяет, является ли переданная строка корректным email-адресом.
    :param email: Строка, содержащая email-адрес.
    :return: True, если email-адрес корректен, иначе False.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))


def valid_time(time_text):
    for fmt in ["%H:%M", "%H-%M"]:
        try:
            time = datetime.strptime(time_text, fmt)
            if 0 <= time.hour <= 23 and 0 <= time.minute <= 59:
                return time.strftime("%H:%M")
        except ValueError:
            pass
    return None


def validate_date(date_text):
    try:
        date_obj = datetime.strptime(date_text, "%d-%m-%Y").date()
        if date_obj < date.today():
            return False, "Выбранная дата в прошлом. Введите дату в формате ДД-ММ-ГГГГ не раньше сегодняшнего дня"
        return True, date_obj
    except ValueError:
        return False, "Неправильный формат даты. Пожалуйста, введите дату в формате ДД-ММ-ГГГГ"


async def validate_user_id(user_id: str) -> bool:
    try:
        user_id = int(user_id)
        if user_id <= 0:
            raise ValueError
        user = await get_user(user_id)
        print(user)
        if not user:
            raise ValueError
        return True
    except ValueError:
        return False
