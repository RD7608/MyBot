from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta


def inline_keyboard_calendar():
    keyboard = InlineKeyboardMarkup(row_width=3)
    current_date = datetime.now()
    for i in range(9):
        button_date = current_date + timedelta(days=i)
        keyboard.insert(InlineKeyboardButton(button_date.strftime('%d-%m-%Y'), callback_data=f"date_{button_date.strftime('%d-%m-%Y')}"))
#    keyboard.add(InlineKeyboardButton("Задать дату вручную", callback_data="date_manual"))
    return keyboard


def kb_type_reminder():
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton(text="Задача", callback_data="task"))
    keyboard.insert(InlineKeyboardButton(text="Встреча", callback_data="meeting"))
    return keyboard


def kb_show_reminders():
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('➕ Добавить', callback_data='add_reminder'))
    keyboard.insert(InlineKeyboardButton('❌ Удалить', callback_data='delete_reminder'))
#   keyboard.add(InlineKeyboardButton('Удалить все', callback_data='delete_all_reminders'))
    return keyboard


