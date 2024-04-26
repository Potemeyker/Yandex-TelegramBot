import logging

from database import add_user, find_user, search_film

from telegram import ReplyKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

BOT_TOKEN = "6471385855:AAEE0HX4cAbt8GJ15ZsxD35Mw5cc643UCBU"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

# logger = logging.getLogger(__name__)


async def start(update, context):
    keyboard = [
        ["🔍 Начать поиск"],
        ["💡 Инструкция"]
    ]

    user_id = update.message.from_user.id

    if find_user(user_id) is None:
        add_user(user_id)

    await update.message.reply_text(
        "🍿 Привет, киноман!\n\n"
        "🔍 Для поиска используй кнопки ниже или отправь в сообщении название кино",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True))


async def reply(update, context):
    response = update.message.text

    if response == "🔍 Начать поиск":
        await update.message.reply_text(
            'Чтобы найти нужное кино просто отправь в сообщении свой запрос\n\n'
            '<i>если не получилось - читай инструкцию</i>',
            parse_mode=ParseMode.HTML)
    elif response == "💡 Инструкция":
        await update.message.reply_text("ЧТО ПОЗВОЛЯЕТ ДЕЛАТЬ БОТ?\n\n"
                                        "С помощью бота ты сможешь искать фильм или сериал, смотреть его, добавлять в "
                                        "избранное, скачивать и смотреть офлайн!\n\n\n"
                                        "КАК ПОЛЬЗОВАТЬСЯ БОТОМ?\n\n"
                                        "🔍 Отправь боту название кино и бот выдаст результат поиска, примеры:\n"
                                        "✅ бесстыжие\n"
                                        "✅ довод")
    else:
        film = search_film(response)
        if film:
            await update.message.reply_video(
                film.path,
                caption=f"{film.name}\n\n"
            )
        else:
            await update.message.reply_text("Фильм не найден")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    application.run_polling()


if __name__ == '__main__':
    main()
