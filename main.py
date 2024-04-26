import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters
from telegram.constants import ParseMode

BOT_TOKEN = "7036753504:AAFm3lyztMcnPQFdsqts6xY7giMkfA2SHhY"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update, context):
    keyboard = [
        ["🔍 Начать поиск"],
        ["💡 Инструкция"]
    ]

    await update.message.reply_text(
        "🍿 Привет, киноман!\n\n"
        "🔍 Для поиска используй кнопки ниже или отправь в сообщении название кино",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True))


async def reply(update, context):
    response = update.message.text

    if response == "🔍 Начать поиск":
        await update.message.reply_text("Выполняется поиск")
    elif response == "💡 Инструкция":
        await update.message.reply_text("ЧТО ПОЗВОЛЯЕТ ДЕЛАТЬ БОТ?\n\n"
                                        "С помощью бота ты сможешь искать фильм или сериал, смотреть его, добавлять в "
                                        "избранное, скачивать и смотреть офлайн!\n\n\n"
                                        "КАК ПОЛЬЗОВАТЬСЯ БОТОМ?\n\n"
                                        "🔍 Отправь боту название кино и бот выдаст результат поиска, примеры:\n"
                                        "✅ бесстыжие\n"
                                        "✅ довод")
    else:
        await update.message.reply_text("Выполняется поиск")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    application.run_polling()


if __name__ == '__main__':
    main()
