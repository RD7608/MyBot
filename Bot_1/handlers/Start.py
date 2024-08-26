import texts.start
from keyboards import *
import database


async def start(message):
    database.add(message.from_user.id)
    await message.answer(f'✅ Добро пожаловать, @{message.from_user.username}!\n\n' + texts.start.start, parse_mode='HTML', reply_markup=start_kb)


async def about_as(message):
    with open('files/media/about.jpg', "rb") as img:
        await message.answer_photo(img, texts.start.about_as, parse_mode='HTML', reply_markup=start_kb)


async def ban_message(update):
    await update.answer(texts.admin.ban, parse_mode='HTML')


async def ban_callbackquery(update):
    await update.message.answer(texts.admin.ban, parse_mode='HTML')
    await update.answer()