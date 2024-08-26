from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from datetime import datetime

from database import ban_user, unban_user, get_user, get_reminders
from utils import validate_user_id, is_admin


class UserState(StatesGroup):
    user_id = State()
    reason = State()
    Ban = None


async def admin_panel(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Пользователи", callback_data="users"))
    keyboard.add(types.InlineKeyboardButton("Статистика", callback_data="stats"))
    await message.answer("Выберите раздел:", reply_markup=keyboard)


async def users_callback(callback: types.CallbackQuery):
    users = await get_user()
    user_list = "\n".join([f"{user_id} - {username} - {'Заблокирован' if ban==1 else 'Активен'}" for user_id, username, email, reg_date, ban, *_ in users])
    keyboard = types.InlineKeyboardMarkup()
    keyboard.insert(types.InlineKeyboardButton("Блокировать", callback_data="block"))
    keyboard.insert(types.InlineKeyboardButton("Разблокировать", callback_data="unblock"))
    await callback.message.answer(user_list, reply_markup=keyboard)


async def stats_callback(callback: types.CallbackQuery):
    users = await get_user()
    reminders = await get_reminders()
    total_users = len(users)
    blocked_users = sum(1 for user in users if user[3] == 1)
    total_reminders = len(reminders)
    sent_reminders = sum(1 for reminder in reminders if reminder[2] == 1)
    stats = f"Всего пользователей: {total_users}\nЗаблокированных пользователей: {blocked_users}\nВсего напоминаний: {total_reminders}\nОтправленных напоминаний: {sent_reminders}"
    await callback.message.answer(stats)


async def user_callback(call: types.CallbackQuery):
    print(call.data)
    if call.data.startswith("block"):
        # Здесь должна быть логика блокировки пользователя
        await call.message.answer("Пожалуйста, введите ID пользователя, которого хотите заблокировать.")
        await UserState.user_id.set()
        UserState.Ban = 1
    elif call.data.startswith("unblock"):
        # Здесь должна быть логика разблокировки пользователя
        await call.message.answer("Пожалуйста, введите ID пользователя, которого хотите разблокировать.")
        await UserState.user_id.set()
        UserState.Ban = 0


async def get_user_id(message: types.Message, state: FSMContext):
    user_id = message.text
    if not await validate_user_id(user_id):
        await message.answer("Некорректный user_id или пользователь не существует.")
        return
    await set_user_id(message, state)


async def set_user_id(message: types.Message, state: FSMContext = None):
    try:
        user_id = int(message.text)
        if is_admin(user_id):
            await message.answer("Это администратор! недоступно")
            await message.answer("Введите другой id")
            return
        if state:
            async with state.proxy() as data:
                data['user_id'] = user_id
        await message.answer("Введите причину блокировки/разблокировки:")
        if state:
            await UserState.next()
    except ValueError:
        await message.answer("Неправильный формат user_id. Введите целое число.")


async def set_reason(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data['user_id']
        reason = message.text
        date = datetime.now().strftime('%d-%m-%Yd %H:%M:%S')
        if UserState.Ban == 1:
            await ban_user(user_id, reason, date)
            await message.answer(f"Пользователь {user_id} заблокирован.")
        elif UserState.Ban == 0:
            await unban_user(user_id, reason, date)
            await message.answer(f"Пользователь {user_id} разблокирован.")
        else:
            await message.answer("Неверная команда. Попробуйте ещё раз.")
            return
    await state.finish()


async def cancel_callback(callback: types.CallbackQuery):
    await callback.message.answer("Операция отменена.")
    await callback.message.delete()
