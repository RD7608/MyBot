from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Клавиатура для главного меню
kb_start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📌 О нас'), KeyboardButton(text='👤 Профиль')
        ],
        [
            KeyboardButton(text='🛒 Заказать'), KeyboardButton(text='📝 Мои заказы')
        ]
    ], resize_keyboard=True, input_field_placeholder="Сделайте выбор:"
)


# Кнопка "Отмена"
def get_kb_cancel(str_cancel):
    kb_cancel = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = InlineKeyboardButton(text='Отмена', callback_data='cancel_registration')
    kb_cancel.add(buttons)
    return kb_cancel


# Клавиатура для каталога
def get_kb_products(products):
    kb_products = InlineKeyboardMarkup(resize_keyboard=True)
    buttons = [InlineKeyboardButton(text=product[1], callback_data=f'product_{product[0]}') for product in products]
    kb_products.add(*buttons)
    return kb_products
