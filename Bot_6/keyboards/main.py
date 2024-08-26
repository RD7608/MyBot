from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu(is_admin=False):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("Добавить напоминание"))
    keyboard.add(KeyboardButton("Просмотреть список"))
    if is_admin:
        keyboard.add(KeyboardButton("⭐Админ панель"))
    return keyboard
