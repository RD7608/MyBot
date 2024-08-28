import logging
import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()

API = os.getenv("API")
ADMINS = eval(os.getenv("ADMINS"))


# Настраиваем логгер
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a',
                    encoding='utf-8')


bot = Bot(token=API, parse_mode='HTML')