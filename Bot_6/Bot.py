import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommandScopeDefault, BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import init_db
import handlers.start
import handlers.reminders
import handlers.admin
from utils import send_reminders
from config import bot, ADMINS

# Настраиваем логгер
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a',
                    encoding='utf-8')
logger = logging.getLogger(__name__)


dp = Dispatcher(bot, storage=MemoryStorage())

# Регистрация handler'ов
dp.message_handler(commands=['start'])(handlers.start.start)
dp.message_handler(commands=['remind'])(handlers.reminders.show_reminders)
dp.message_handler(commands=['del'])(handlers.reminders.del_message)
#dp.message_handler(commands=['info'])(handlers.start.info)

#dp.message_handler(text='Регистрация', state=None)(handlers.start.register_user)
dp.message_handler(state=handlers.start.RegistrationState.name)(handlers.start.process_name)
dp.message_handler(state=handlers.start.RegistrationState.email)(handlers.start.process_email)

dp.message_handler(text='Добавить напоминание')(handlers.reminders.process_add_task)
dp.callback_query_handler(lambda qt: qt.data == 'task' or qt.data == 'meeting',
                          state=handlers.reminders.ReminderState.event_type)(handlers.reminders.set_event_type)
dp.message_handler(state=handlers.reminders.ReminderState.event_name)(handlers.reminders.set_event_name)
dp.callback_query_handler(lambda qd: qd.data.startswith('date_'),
                          state=handlers.reminders.ReminderState.event_date)(handlers.reminders.set_event_date)
dp.message_handler(state=handlers.reminders.ReminderState.event_time)(handlers.reminders.set_event_time)
dp.callback_query_handler(state=handlers.reminders.ReminderState.event_message)(handlers.reminders.enter_text_reminder)
dp.message_handler(state=handlers.reminders.ReminderState.event_message)(handlers.reminders.set_event_message)

dp.message_handler(text='Просмотреть список')(handlers.reminders.show_reminders)
dp.callback_query_handler(text=['add_reminder', 'delete_reminder', 'delete_all_reminders'])(
    handlers.reminders.process_callback_query)
dp.message_handler(lambda message: message.text.isdigit(),
                   state=handlers.reminders.EnterNumberState.enter_number)(handlers.reminders.process_message)

dp.message_handler(text='⭐Админ панель')(handlers.admin.admin_panel)
dp.callback_query_handler(text="users")(handlers.admin.users_callback)
dp.callback_query_handler(text="stats")(handlers.admin.stats_callback)
dp.callback_query_handler(text='block')(handlers.admin.user_callback)
dp.callback_query_handler(text='unblock')(handlers.admin.user_callback)
dp.message_handler(state=handlers.admin.UserState.user_id)(handlers.admin.get_user_id)
dp.message_handler(state=handlers.admin.UserState.reason)(handlers.admin.set_reason)

dp.message_handler(content_types=types.ContentTypes.ANY)(handlers.start.unknown_message)
dp.errors_handler(exception=Exception)(handlers.start.global_error_handler)


async def set_commands():
    commands = [
        BotCommand(command='start', description='Главное меню'),
        BotCommand(command='info', description='Информация'),
        BotCommand(command='remind', description='Список напоминаний')
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def on_startup(_):
    await init_db()
    await set_commands()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_reminders, 'cron', minute='*')  # запускать каждую минуту
    scheduler.start()

#    await bot.send_message(chat_id=ADMINS[0], text="Бот запущен!")


async def on_shutdown(_):
    await bot.send_message(chat_id=ADMINS[0], text="Бот выключен!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
