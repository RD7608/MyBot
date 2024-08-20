import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

import database
from handlers import User

from config import *


# Настраиваем логгер
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a',
                    encoding='utf-8')
logger = logging.getLogger(__name__)

api = API

bot = Bot(token=api, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())

# Инициализируем базу данных
database.initiate_db()

# Регистрация handler'ов
dp.message_handler(commands=['start'])(User.start)
dp.message_handler(commands=['info'])(User.info)
dp.message_handler(text='📌 О нас')(User.info)
dp.message_handler(text='👤 Профиль', state=None)(User.profile)

dp.message_handler(state=User.RegistrationState.username)(User.set_username)
dp.message_handler(state=User.RegistrationState.email)(User.set_email)
dp.message_handler(state=User.RegistrationState.sity)(User.set_age)
dp.callback_query_handler(text='cancel_registration', state='*')(User.cancel_registration)

dp.message_handler(text='🛒 Заказать')( User.new_order_request)
dp.callback_query_handler(text_startswith='product_')(User.send_confirm_message)

# dp.message_handler(text='📝 Мои заказы')( User.my_orders )

# dp.message_handler(text='🔙 Назад')( User.back_to_main_menu )

dp.message_handler(content_types=types.ContentTypes.ANY)( User.unknown_message )
dp.errors_handler(exception=Exception)( User.global_error_handler )


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


if __name__ == '__main__':

    executor = executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
#    executor.start_polling(dp, skip_updates=True)
