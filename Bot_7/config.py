import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()

API = os.getenv("API")
ADMINS = eval(os.getenv("ADMINS"))

bot = Bot(token=API, parse_mode='HTML')