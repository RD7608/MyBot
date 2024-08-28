import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault


import database
from handlers import Start
from handlers import User
from handlers import Admin
import utils
from config import bot


logger = logging.getLogger(__name__)

dp = Dispatcher(bot, storage=MemoryStorage())

# Инициализируем базу данных
database.initiate_db()

#dp.message_handler(lambda m: database.check_block(m.from_user.id))(Start.ban_message)
#dp.callback_query_handler(lambda c: database.check_block(c.from_user.id))(Start.ban_callbackquery)

# Регистрация handler'ов
dp.message_handler(commands=['start'])(User.start)
dp.message_handler(commands=['info'])(User.info)
dp.message_handler(text='📌 О нас')(User.info)
dp.message_handler(text='👤 Профиль', state=None)(User.profile)

dp.message_handler(state=User.RegistrationState.username)(User.set_username)
dp.message_handler(state=User.RegistrationState.email)(User.set_email)
dp.message_handler(state=User.RegistrationState.sity)(User.set_age)
dp.callback_query_handler(text='cancel_registration', state='*')(User.cancel_registration)

dp.message_handler(text='🛒 Заказать')(User.new_order_request)
dp.callback_query_handler(text_startswith='city_')(User.city_selected)
dp.callback_query_handler(text_startswith='product_')(User.send_confirm_message)

dp.message_handler(text='📝 Мои заказы')(User.view_orders)
dp.callback_query_handler(text_startswith='orders_')(User.orders_callback)

# dp.message_handler(text='🔙 Назад')( User.back_to_main_menu )

dp.message_handler(content_types=types.ContentTypes.ANY)(User.unknown_message)
dp.errors_handler(exception=Exception)(User.global_error_handler)



async def set_commands():
    commands = [
        BotCommand(command='start', description='Главное меню'),
        BotCommand(command='info', description='Информация'),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def on_startup(_):
    logger.info('Бот запущен')
    await set_commands()


async def on_shutdown(_):
    logger.info('Бот выключен')


# Планирование задачи
import schedule
import time
schedule.every().day.at("08:00").do(utils.send_notifications)  # вызов функции в 8:00 каждый день

while True:
    schedule.run_pending()
    time.sleep(1)



if __name__ == '__main__':

    executor = executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
#    executor.start_polling(dp, skip_updates=True)
