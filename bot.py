import json
import logging

from telegram._files import voice

from database import add_user, find_user, search_film

from telegram import ReplyKeyboardMarkup, InputFile, InlineKeyboardButton, InlineKeyboardMarkup, InputMedia
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from telegram.constants import ParseMode

BOT_TOKEN = "6471385855:AAEE0HX4cAbt8GJ15ZsxD35Mw5cc643UCBU"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

NEW_SEARCH, SEARCH, INSTRUCTION, SHOW, VOICES, QUALITY, PREVIOUS, NEXT, SERIES = map(str, range(9))


async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("💡 Инструкция", callback_data=INSTRUCTION)],
    ]

    user_id = update.message.from_user.id

    if find_user(user_id) is None:
        add_user(user_id)

    await update.message.reply_text(
        "🍿 Привет, киноман!\n\n"
        "🔍 Для поиска отправь в сообщении название кино\n\n"
        "<i>если не получилось - читай инструкцию</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard))


async def new_search(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("💡 Инструкция", callback_data=INSTRUCTION)],
    ]

    await query.delete_message()
    await query.message.reply_text(
        "🔍 Для поиска отправь в сообщении название кино\n\n"
        "<i>если не получилось - читай инструкцию</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard))


async def search(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("💡 Инструкция", callback_data=INSTRUCTION)],
    ]

    await query.edit_message_text(
        "🔍 Для поиска отправь в сообщении название кино\n\n"
        "<i>если не получилось - читай инструкцию</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard))


async def instruction(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("◀️ Назад", callback_data=SEARCH)],
    ]

    await query.edit_message_text("ЧТО ПОЗВОЛЯЕТ ДЕЛАТЬ БОТ?\n\n"
                                  "С помощью бота ты сможешь искать фильм или сериал, смотреть его, добавлять в"
                                  "избранное, скачивать и смотреть офлайн!\n\n\n"
                                  "КАК ПОЛЬЗОВАТЬСЯ БОТОМ?\n\n"
                                  "🔍 Отправь боту название кино и бот выдаст результат поиска, примеры:\n"
                                  "✅ бесстыжие\n"
                                  "✅ довод",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def reply(update, context):
    response = update.message.text

    movie = search_film(response)
    if movie:
        with open(f"data/{movie.id}.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)

        voice = "Русский"
        quality = "480"

        context.user_data["voice"] = voice
        context.user_data["quality"] = quality
        context.user_data["movie_json"] = json_data

        if json_data["type"] == 0:
            keyboard = [
                [
                    InlineKeyboardButton("Озвучка", callback_data=VOICES),
                    InlineKeyboardButton("Качество", callback_data=QUALITY)
                ],
                [InlineKeyboardButton("Назад", callback_data=NEW_SEARCH)]
            ]

            movie_url = json_data["voices"][voice][quality]
        else:
            keyboard = [
                [
                    InlineKeyboardButton("Предыдущая", callback_data=PREVIOUS),
                    InlineKeyboardButton("Следующая", callback_data=NEXT)
                ],
                [InlineKeyboardButton("Выбор серии", callback_data=SERIES)],
                [
                    InlineKeyboardButton("Озвучка", callback_data=VOICES),
                    InlineKeyboardButton("Качество", callback_data=QUALITY)
                ],
                [InlineKeyboardButton("Назад", callback_data=SEARCH)]
            ]

            series = "1e1"

            context.user_data["series"] = series
            movie_url = json_data["voices"][voice][quality]["series"][series]

        await update.message.reply_video(
            movie_url,
            caption=f"{movie.name} ({voice} | {quality})\n\n"
                    f"by @YandexKinoBot",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        keyboard = [
            [InlineKeyboardButton("💡 Инструкция", callback_data=INSTRUCTION)],
        ]

        await update.message.reply_text("Фильм не найден\n\n"
                                        "🔍 Для поиска отправь в сообщении название кино\n\n"
                                        "<i>если не получилось - читай инструкцию</i>",
                                        parse_mode=ParseMode.HTML,
                                        reply_markup=InlineKeyboardMarkup(keyboard))


async def show_movie(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data.split()[-1]

    if data.isnumeric():
        context.user_data["quality"] = data
    else:
        context.user_data["voice"] = data

    voice = context.user_data["voice"]
    quality = context.user_data["quality"]
    series = None
    caption = None
    movie_json = context.user_data["movie_json"]

    if movie_json["type"] == 0:
        keyboard = [
            [
                InlineKeyboardButton("Озвучка", callback_data=VOICES),
                InlineKeyboardButton("Качество", callback_data=QUALITY)
            ],
            [InlineKeyboardButton("Назад", callback_data=NEW_SEARCH)]
        ]

        caption = (f"{movie_json["name"]} ({voice} | {quality}p)\n\n"
                   f"by @YandexKinoBot")
    else:
        keyboard = [
            [
                InlineKeyboardButton("Предыдущая", callback_data=PREVIOUS),
                InlineKeyboardButton("Следующая", callback_data=NEXT)
            ],
            [InlineKeyboardButton("Выбор серии", callback_data=SERIES)],
            [
                InlineKeyboardButton("Озвучка", callback_data=VOICES),
                InlineKeyboardButton("Качество", callback_data=QUALITY)
            ],
            [InlineKeyboardButton("Назад", callback_data=NEW_SEARCH)]
        ]

        caption = (f"{movie_json["name"]} ({voice} | {quality})\n"
                   f"\n"
                   f"by @YandexKinoBot")

    media_type = "video"
    try:
        movie_url = movie_json["voices"][voice][quality]
    except KeyError:
        media_type = "photo"
        movie_url = movie_json["poster"]
        caption = (f"{movie_json["name"]} ({voice} | {quality}p)\n\n"
                   f"Фильм в таких озвучке и качестве ещё не вышел\n\n\n"
                   f"by @YandexKinoBot")

    await query.edit_message_media(InputMedia(media_type, movie_url))
    await query.edit_message_caption(caption)
    await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))


async def change_voices(update, context):
    query = update.callback_query
    await query.answer()

    voices = get_voices(context.user_data["movie_json"])

    keyboard = [[InlineKeyboardButton(voice, callback_data=f"{SHOW} {voice}")] for voice in voices]
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data=SHOW)])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))


def get_voices(json_data):
    return list(json_data["voices"].keys())


async def change_quality(update, context):
    query = update.callback_query
    await query.answer()

    qualities = get_qualities(context.user_data["movie_json"], context.user_data["voice"])

    print(qualities)

    keyboard = [[InlineKeyboardButton(quality, callback_data=f"{SHOW} {quality}")] for quality in qualities]
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data=SHOW)])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))


def get_qualities(json_data, voice):
    return list(json_data["voices"][voice].keys())


async def change_series(update, context):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(text="Выбор серии")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    application.add_handler(CallbackQueryHandler(search, pattern=f"^{SEARCH}$"))
    application.add_handler(CallbackQueryHandler(new_search, pattern=f"^{NEW_SEARCH}$"))
    application.add_handler(CallbackQueryHandler(instruction, pattern=f"^{INSTRUCTION}$"))
    application.add_handler(CallbackQueryHandler(show_movie, pattern=f"^{SHOW}.*$"))
    application.add_handler(CallbackQueryHandler(change_voices, pattern=f"^{VOICES}$"))
    application.add_handler(CallbackQueryHandler(change_quality, pattern=f"^{QUALITY}$"))
    application.add_handler(CallbackQueryHandler(change_series, pattern=f"^{SERIES}$"))

    application.run_polling()


if __name__ == '__main__':
    main()
