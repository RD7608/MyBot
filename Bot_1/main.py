import logging
import asyncio

from aiogram import Bot , Dispatcher , executor , types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand , BotCommandScopeDefault

import database
import config
import User
import Admin
import Manage

# Настраиваем логгер
logging.basicConfig ( level=logging.INFO ,
                      format='%(asctime)s - %(levelname)s - %(message)s' ,
                      filename='bot.log' ,
                      filemode='a' ,
                      encoding='utf-8' )
logger = logging.getLogger ( __name__ )

api = config.API

bot = Bot ( token=api , parse_mode='HTML' )
dp = Dispatcher(bot, storage=MemoryStorage())

# Инициализируем базу данных
database.initiate_db ()

# Регистрация handler'ов
dp.message_handler(commands=['start'])(User.start)
dp.message_handler(commands=['info'])(User.info)
dp.message_handler(text='📌 О нас')(User.info)
dp.message_handler(text='👤 Профиль', state=None)(User.profile)

dp.message_handler(state=User.RegistrationState.username)(User.set_username)
dp.message_handler(state=User.RegistrationState.email)(User.set_email)
dp.message_handler(state=User.RegistrationState.age)(User.set_age)
dp.callback_query_handler(text='cancel_registration', state='*')(User.cancel_registration)

dp.message_handler(text='🛒 Заказать')(User.new_order_request)
dp.callback_query_handler(text_startswith='product_')(User.send_confirm_message)

dp.message_handler(text='📝 Мои заказы')(User.my_orders)
dp.callback_query_handler ( text='calories' ) ( User.get_calories )
dp.message_handler ( state=User.UserState.age ) ( User.set_user_age )
dp.message_handler ( state=User.UserState.growth ) ( User.set_user_growth )
dp.message_handler ( state=User.UserState.weight ) ( User.set_user_weight )

dp.callback_query_handler ( text='formulas' ) ( User.get_formulas )

dp.message_handler( content_types=types.ContentTypes.ANY)(User.unknown_message)
dp.errors_handler(exception=Exception)(User.global_error_handler)


async def set_commands():
    commands = [
        BotCommand ( command='start' , description='Главное меню' ) ,
        BotCommand ( command='info' , description='Информация' ) ,
    ]
    await bot.set_my_commands ( commands , scope=BotCommandScopeDefault () )


async def on_startup(_):
    logger.info('Бот запущен')
    await set_commands()


async def on_shutdown(_):
    logger.info('Бот выключен')


if __name__ == '__main__':

    executor = executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
#    executor.start_polling(dp, skip_updates=True)
