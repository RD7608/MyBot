import logging
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

import database
import handlers
import config

# Настраиваем логгер
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='bot.log',
                    filemode='a',
                    encoding='utf-8')

api = config.API

bot = Bot(token=api, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())

# Инициализируем базу данных
database.initiate_db()


# Регистрация handler'ов
dp.message_handler(commands=['start'])(handlers.start)
dp.message_handler(text='📌 О нас')(handlers.show_info)
dp.message_handler(text='👤 Профиль', state=None)(handlers.sing_up)
dp.message_handler(state=handlers.RegistrationState.username)(handlers.set_username)
dp.message_handler(state=handlers.RegistrationState.email)(handlers.set_email)
dp.message_handler(state=handlers.RegistrationState.age)(handlers.set_age)
dp.callback_query_handler(text='cancel_registration', state='*')(handlers.cancel_registration)

dp.message_handler(text='🛒 Заказать')(handlers.get_buying_list)
dp.callback_query_handler(text_startswith='product_buying_')(handlers.send_confirm_message)

dp.message_handler(text='📝 Мои заказы')(handlers.main_menu)
dp.callback_query_handler(text='calories')(handlers.get_calories)
dp.message_handler(state=handlers.UserState.age)(handlers.set_user_age)
dp.message_handler(state=handlers.UserState.growth)(handlers.set_user_growth)
dp.message_handler(state=handlers.UserState.weight)(handlers.set_user_weight)

dp.callback_query_handler(text='formulas')(handlers.get_formulas)

dp.message_handler(content_types=types.ContentTypes.ANY)(handlers.unknown_message)
dp.errors_handler(exception=Exception)(handlers.global_error_handler)


async def set_commands():
    commands = [
        BotCommand(command='start', description='Главное меню'),
        BotCommand(command='info', description='Информация'),
        BotCommand(command='buy', description='Купить'),
        BotCommand(command='reg', description='Регистрация'),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


if __name__ == '__main__':
    logging.info('Бот запущен')
    loop = asyncio.get_event_loop()
    loop.create_task(set_commands())

    executor.start_polling(dp, skip_updates=True, loop=loop)
