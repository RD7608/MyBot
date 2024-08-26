import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database import add_reminder, get_reminders, del_reminder, del_all_reminders
from utils import valid_time, validate_date
from keyboards.inline import inline_keyboard_calendar, kb_show_reminders, kb_type_reminder

logger = logging.getLogger(__name__)


class ReminderState(StatesGroup):
    event_type = State()
    event_name = State()
    event_date = State()
    event_time = State()
    event_message = State()
    confirm = State()


class EnterNumberState(StatesGroup):
    enter_number = State()


async def process_add_task(message: types.Message):
    logger.info(message.text)
    await message.answer("Выберите тип напоминания:", reply_markup=kb_type_reminder())
    await ReminderState.event_type.set()


async def set_event_type(call: types.CallbackQuery, state: FSMContext):
    logger.info(call.data)
    await call.message.delete()

    async with state.proxy() as data:
        if call.data == 'task':
            await call.message.answer("<b>Введите название для задачи</b>:")
            data['event_type'] = 'Задача'
        elif call.data == 'meeting':
            await call.message.answer(f"<b>Введите название для встречи:</b>")
            data['event_type'] = 'Встреча'
        else:
            await call.message.answer("Введите название события:")
            data['event_type'] = call.data
    await ReminderState.next()


async def set_event_name(message: types.Message, state: FSMContext):
    logger.info(message.text)
    async with state.proxy() as data:
        data['event_name'] = message.text

    await message.answer("Выберите дату события:", reply_markup=inline_keyboard_calendar())
    await ReminderState.next()


async def set_event_date(call: types.CallbackQuery, state: FSMContext):
    print("дата", call.data)
    async with state.proxy() as data:
        if call.data == 'date_manual':
            await call.message.answer("Введите дату события (в формате ДД-ММ-ГГГГ):")
            await ReminderState.event_date.set()
            date_text = call.data
            is_valid, result = validate_date(date_text)
            if not is_valid:
                await call.message.answer(result)
                return
            data['event_date'] = result
        else:
            date_text = call.data.split("_")[1]
            is_valid, result = validate_date(date_text)
            if not is_valid:
                await call.message.answer(result)
                return
            data['event_date'] = result
    print(data['event_date'])
    await call.message.delete()
    await call.message.answer("Введите время события (в формате ЧЧ:ММ или ЧЧ-ММ):")
    await ReminderState.next()


async def set_event_time(message: types.Message, state: FSMContext):
    print("time", message.text)
    async with state.proxy() as data:
        event_time = valid_time(message.text)
        if event_time:
            data['event_time'] = event_time
        else:
            await message.answer(
                "Неправильный формат/недопустимое время. Пожалуйста, введите время в формате ЧЧ:ММ или ЧЧ-ММ и от 00:00 до 23:59")
            return

    print(data['event_time'])
    keyboard = types.InlineKeyboardMarkup()
    skip_button = types.InlineKeyboardButton('или пропустить', callback_data='skip_text')
    keyboard.add(skip_button)
    await message.answer("Введите текст напоминания:", reply_markup=keyboard)
    await ReminderState.next()


async def enter_text_reminder(call: types.CallbackQuery, state: FSMContext):
    logger.info(call.data)
    user_id = call.from_user.id
    if call.data == 'skip_text':
        async with state.proxy() as data:
            data['event_message'] = ''
        await call.message.delete()
        await save_reminder(call.message, state)
#        await call.message.answer("✔ Напоминание добавлено!")
#        await state.finish()


async def set_event_message(message: types.Message, state: FSMContext):
    logger.info(message.text)
    user_id = message.from_user.id
    async with state.proxy() as data:
        data['event_message'] = message.text

    await save_reminder(message, state)
#    await message.answer("✔ Напоминание добавлено!")
#    await state.finish()


async def save_reminder(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(
            f"Напоминание:\n"
            f"{data['event_type']} - {data['event_name']}\n"
            f"запланировано на {data['event_date']} в {data['event_time']}\n"
            f"Текст: {data['event_message']}\n\n"
            "<b>Подтвердить создание напоминания?</b>",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("✔️ Да", callback_data="confirm")],
                    [InlineKeyboardButton("❌ Нет", callback_data="cancel")]
                ]
            )
        )
        await ReminderState.next()


async def confirm_reminder(call: types.CallbackQuery, state: FSMContext):
    logger.info(call.data)
    if call.data == "confirm":
        user_id = call.from_user.id
        async with state.proxy() as data:
            await add_reminder(user_id, data)
#        await add_reminder(user_id, event_type, event_name, event_date, event_time, event_message)

        logger.info(str(data))

        await call.message.answer("✔Напоминание успешно создано!")

    else:
        await call.message.answer("❗Напоминание отменено.")
    await call.message.delete()
    await state.finish()


async def show_reminders(message: types.Message):
    user_id = message.from_user.id
    reminders = await get_reminders(user_id)
    if reminders:
        for reminder in reminders:
            await message.answer(f"<b>Номер: {reminder[0]}</b>|"
                                 f" {reminder[2]} |"
                                 f" {reminder[3]} |"
                                 f" {reminder[6]} |"
                                 f"план: {reminder[4]} в {reminder[5]} \n")

        await message.answer('Выберите действие:', reply_markup=kb_show_reminders())

    else:
        await message.answer("Нет запланированных напоминаний.")


async def process_callback_query(call: types.CallbackQuery):
    user_id = call.from_user.id
    if call.data == 'add_reminder':
        await process_add_task(call.message)
    elif call.data == 'delete_reminder':
        await call.message.answer("Введите номер события:", reply_markup=types.ForceReply())
        await EnterNumberState.enter_number.set()
    elif call.data == 'delete_all_reminders':
        await del_all_reminders(user_id)
        await call.message.answer("Все напоминания удалены!", reply_markup=types.ReplyKeyboardRemove())

    await call.message.delete()


async def process_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    event_number = message.text
    if await del_reminder(user_id, event_number):
        await message.answer("Событие удалено!")
    else:
        await message.answer("Событие не найдено!")
    await state.finish()


async def del_message(message: types.Message):
    user_id = message.from_user.id
    event_number = message.text.split(' ')[1]
    if await del_reminder(user_id, event_number):
        await message.answer("Событие удалено!")
    else:
        await message.answer("Событие не найдено. Пожалуйста, введите верный номер.")
