from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types


import config
from keyboards import *
import texts.admin
import database


async def start(message: types.Message):
    if message.from_user.id in config.admins:
        await message.answer(texts.admin.start, parse_mode="HTML", reply_markup=AdminPanel)


async def users(call: types.CallbackQuery):
    from main import bot

    t = '''ID, UserName, Name
➖➖➖➖➖➖➖➖➖'''
    num = 0
    flag = False
    await call.message.delete()
    await call.answer()
    for (id, time,) in database.get_all():
        user = await bot.get_chat(id)
        un = user['username']
        if not un:
            database.delete(id)
            continue
        fn = user['first_name']
        num += 1
        if len(t) > 3900:
            if not flag:
                await call.message.edit_text(t, parse_mode="HTML")
                flag = True
            else:
                await call.message.answer(t, parse_mode="HTML")
            t = ''
        t += f'\n{num}. <code>{id}</code> @{un} <b>{fn}</b>'
    await call.message.answer(t, parse_mode="HTML", reply_markup=back_to_admin)


async def statistick(call: types.CallbackQuery):
    await call.message.edit_text(texts.admin.statistick(int(database.count())), parse_mode="HTML", reply_markup=back_to_admin)
    await call.answer()


class admins(StatesGroup):
    ban = State()
    mailing_step1 = State()
    mailing_step2 = State()


async def mailing(call: types.CallbackQuery):
    instructions = "Введите текст сообщения:"
    await call.message.answer(instructions, reply_markup=types.ReplyKeyboardRemove())
    await call.answer()
    await admins.mailing_step1.set()


async def mailing1(message, state):
    await state.update_data(text=message.text)

    instructions = "Прикрепите фотографию к сообщению:"
    await message.answer(text=instructions)

    await admins.mailing_step2.set()


async def mailing2(message, state):
    from main import bot

    await message.photo[-1].download(destination_file='files/photo.jpg')
    data = await state.get_data()
    subscribers = database.get_id()

    c = 0
    for (user_id,) in subscribers:
        try:
            with open('files/photo.jpg', 'rb') as f:
                await bot.send_photo(user_id, f, data['text'])
            c += 1
        except Exception as e:
            print(e)

    await message.answer(f'Рассылка успешно завершена: {c} / {database.count()}', reply_markup=AdminPanel)
    await state.finish()


async def block(call: types.CallbackQuery):
    await call.message.answer(texts.admin.ban_from_admin_start, parse_mode="HTML",
                              reply_markup=types.ReplyKeyboardRemove())
    await call.answer()
    await admins.ban.set()


async def ban1(message, state):
    from main import bot
    
    text = message.text
    if text == '/cancel':
        await message.answer(texts.admin.ban_from_admin_cancel, reply_markup=AdminPanel)
        await state.finish()
        return

    if text.isdigit():
        id = int(text)
        try:
            await bot.send_message(id, texts.admin.ban)
        except Exception as e:
            print(e)
        database.block(id)
        await message.answer(texts.admin.ban_from_admin_finaly, parse_mode='HTML', reply_markup=AdminPanel)
        await state.finish()
    else:
        await message.answer(texts.admin.ban_from_admin_except, parse_mode='HTML')


async def back_admin(call: types.CallbackQuery):
    await call.message.edit_text(texts.admin.start, parse_mode="HTML", reply_markup=AdminPanel)
    await call.answer()
