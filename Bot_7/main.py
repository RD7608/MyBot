import wikipedia
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import webbrowser
from config import bot, ADMINS

# Настройка FSM
dp = Dispatcher(bot, storage=MemoryStorage())

wikipedia.set_lang("ru")


class WikipediaSearch(StatesGroup):
    waiting_for_query = State()
    waiting_for_disambiguation_choice = State()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = "Вот что я умею:\n\n" \
                "/start - запустить бота\n" \
                "/help - показать доступные команды\n" \
                "Просто напишите мне что-нибудь, и я попробую найти информацию в Википедии!"
    await message.answer(help_text)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Я могу помочь тебе найти информацию в Википедии. Просто отправь мне запрос.")


@dp.message_handler()
async def search_wikipedia(message: types.Message):
    query = message.text
    try:
        page = wikipedia.page(query)
        summary = page.summary
        url = page.url

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Полная статья", url=url))
        await message.answer(summary, reply_markup=keyboard)

    except wikipedia.exceptions.PageError:
        await message.reply("Страница не найдена")
    except wikipedia.exceptions.DisambiguationError as e:
        # Получаем список вариантов из ошибки DisambiguationError
        options = e.options
        keyboard = types.InlineKeyboardMarkup()
        for option in options:
            keyboard.add(types.InlineKeyboardButton(text=option, callback_data=f"option_{option}"))
        await message.reply("Уточните ваш запрос:", reply_markup=keyboard)

    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")


@dp.callback_query_handler(text_startswith='option_back')
async def get_back(call):
    await call.answer()


# Обработка нажатия на кнопку с выбором варианта
@dp.callback_query_handler(text_startswith='option_')
async def send_confirm_message(call):
    try:
        q = call.data.split('_')[1]
        print(q)
        # Пытаемся получить информацию по выбранному варианту
        page = wikipedia.page(q)
        summary = page.summary
        url = page.url
        await call.message.answer(summary)
        await call.message.answer(f"Полная статья: {url}")

    except wikipedia.exceptions.PageError:
        await call.message.answer("В Википедии нет информации по этому запросу")
    except wikipedia.exceptions.DisambiguationError as e:
        # Если запрос не найден в Википедии, открываем поиск в Яндексе и Google
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Поиск в Яндексе", callback_data=f"yandex_{q}"))
        keyboard.add(types.InlineKeyboardButton(text="Поиск в Google", callback_data=f"google_{q}"))
        keyboard.add(types.InlineKeyboardButton(text="Либо уточните запрос", callback_data="option_back"))
        await call.message.answer(
            "Извините, не удалось найти информацию по вашему запросу в Википедии. Попробуйте воспользоваться поиском в Яндексе или Google:",
            reply_markup=keyboard)

    except Exception as e:
        await call.message.answer(f"Произошла ошибка: {e}")


@dp.callback_query_handler(text_startswith='yandex_')
async def get_yandex(call):
    query = call.data.split('_')[1]
    webbrowser.open(f"https://yandex.ru/search/?text={query}")
    await call.answer()


@dp.callback_query_handler(text_startswith='google_')
async def get_google(call):
    query = call.data.split('_')[1]
    webbrowser.open(f"https://www.google.com/search?q={query}")
    await call.answer()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
