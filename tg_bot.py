import time
import json
import asyncio
from telegram import ParseMode
from time import localtime, strftime
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BotBlocked
from aiogram import Bot, Dispatcher, types, executor
from main import main, new_user, check_news_update, save_in_json, token


bot = Bot(token=token)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = ["Все новости", "Последние 5 новостей", "Получать свежие новости"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer("Выберите, что хотите увидеть:", parse_mode="Markdown", reply_markup=keyboard)


@dp.message_handler(Text(equals="Все новости"))
async def get_all_news(message: types.Message):
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items()):
        news = f"<b>{(v['article_date_timestamp'])}\n</b>" \
               f"<a href='{(v['article_url'])}'> {'Перейти на сайт'}</a>"
        await message.answer(news, parse_mode=ParseMode.HTML)


@dp.message_handler(Text(equals="Последние 5 новостей"))
async def get_five_news(message: types.Message):
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items())[-5:]:
        news = f"<b>{(v['article_date_timestamp'])}\n</b>" \
               f"<a href='{(v['article_url'])}'> {'Перейти на сайт'}</a>"
        await message.answer(news, parse_mode=ParseMode.HTML)


@dp.message_handler(Text(equals="Получать свежие новости"))
async def get_fresh_news(message: types.Message):
    new_user()
    await check_every_hour()
    loop = asyncio.get_event_loop()
    loop.create_task(check_every_hour())


async def check_every_hour():
    while True:
        try:
            updated_news = check_news_update()
            with open("users_dict.json") as file:
                info = json.load(file)
            user_id = []
            for i in info:
                user_id.append(i['user_id'])
            for each in user_id:
                if len(updated_news) >= 1:
                        for k, v in sorted(updated_news):
                            news = f"<b>{(v['article_date_timestamp'])}\n</b>" \
                                       f"<a href='{(v['article_url'])}'> {'Перейти на сайт'}</a>"
                            await bot.send_message(each, news, parse_mode=ParseMode.HTML)
                            save_in_json()
                            time.sleep(5)
            print("I'm alive! (seclab.ru)")
            print(strftime("%Y-%m-%d %H:%M:%S\n", localtime()))
            await asyncio.sleep(1800)
        except BotBlocked:
            print("--- UserBlocked ---")
            print(strftime("%Y-%m-%d %H:%M:%S\n", localtime()))


if __name__ == '__main__':
    main()
    save_in_json()
    executor.start_polling(dp, skip_updates=True)
