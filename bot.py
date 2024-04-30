import json
import logging

from database import add_user, find_user, search_film

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMedia
from telegram.ext import filters, Application, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.constants import ParseMode

BOT_TOKEN = "6471385855:AAEE0HX4cAbt8GJ15ZsxD35Mw5cc643UCBU"  # токен бота

# логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# переменные константы для вызова определённых функций
NEW_SEARCH, SEARCH, INSTRUCTION, SHOW, VOICES, QUALITY, NONE, SERIES = map(str, range(8))


async def start(update, context):
    """Отправляет приветственное сообщение при вызове команды /start"""
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
    """Создаёт новое сообщение поиска при callback=NEW_SEARCH"""

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
    """Меняет сообщение бота под поиск при callback=SEARCH"""

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
    """Меняет сообщение бота на текст инструкции при callback=INSTRUCTION"""

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data=SEARCH)],
    ]

    await query.edit_message_text("ЧТО ПОЗВОЛЯЕТ ДЕЛАТЬ БОТ?\n\n"
                                  "С помощью бота ты сможешь искать фильм или сериал, смотреть его,"
                                  " скачивать и смотреть офлайн!\n\n\n"
                                  "КАК ПОЛЬЗОВАТЬСЯ БОТОМ?\n\n"
                                  "🔍 Отправь боту название кино и бот выдаст результат поиска, примеры:\n"
                                  "✅ бесстыжие\n"
                                  "✅ довод",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def reply(update, context):
    """При получении сообщения от пользователя обращается к БД для поиска фильма
    Если фильм есть в БД выводит видео и его настройки, иначе выводит сообщение, что фильм не найден"""

    response = update.message.text

    movie = search_film(response)
    if movie:
        with open(f"data/{movie.id}.json", "r", encoding="utf-8") as file:
            movie_json = json.load(file)

        voice = "Русский"
        quality = "480"

        context.user_data["voice"] = voice
        context.user_data["quality"] = quality
        context.user_data["movie_json"] = movie_json

        if movie_json["type"] == 0:
            keyboard = [
                [
                    InlineKeyboardButton("🔊 Озвучка", callback_data=VOICES),
                    InlineKeyboardButton("🔮 Качество", callback_data=QUALITY)
                ],
                [InlineKeyboardButton("🔙 Назад", callback_data=NEW_SEARCH)]
            ]

            movie_url = movie_json["videos"][voice][quality]
            caption = (f"{movie_json["name"]} ({voice} | {quality}p)\n\n"
                       f"by @YandexKinoBot")
        else:
            keyboard = [
                [
                    InlineKeyboardButton("✖️ Предыдущая", callback_data=NONE),
                    InlineKeyboardButton("➡️ Следующая", callback_data=f"{SHOW} series 1e2")
                ],
                [InlineKeyboardButton("🔢 Выбор серии", callback_data=f"{SERIES} voice")],
                [
                    InlineKeyboardButton("🔊 Озвучка", callback_data=VOICES),
                    InlineKeyboardButton("🔮 Качество", callback_data=QUALITY)
                ],
                [InlineKeyboardButton("🔙 Назад", callback_data=SEARCH)]
            ]

            series = "1e1"
            context.user_data["series"] = series

            movie_url = movie_json["videos"][series][voice][quality]
            caption = (f"{movie_json["name"]} ({voice} | {quality}p)\n" +
                       "сезон {} серия {}\n\n".format(*series.split('e')) +
                       f"by @YandexKinoBot")

        await update.message.reply_video(
            movie_url,
            caption=caption,
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
    """Выводит видео и его настройки при callback=SHOW"""

    query = update.callback_query
    await query.answer()

    try:
        _, name, data = query.data.split()
        context.user_data[name] = data
    except ValueError:
        pass

    voice = context.user_data["voice"]
    quality = context.user_data["quality"]
    movie_json = context.user_data["movie_json"]

    if movie_json["type"] == 0:
        keyboard = [
            [
                InlineKeyboardButton("🔊 Озвучка", callback_data=VOICES),
                InlineKeyboardButton("🔮 Качество", callback_data=QUALITY)
            ],
            [InlineKeyboardButton("🔙 Назад", callback_data=NEW_SEARCH)]
        ]

        try:
            media_type = "video"
            movie_url = movie_json["videos"][voice][quality]
            caption = (f"{movie_json["name"]} ({voice} | {quality}p)\n\n"
                       f"by @YandexKinoBot")
        except KeyError:
            media_type = "photo"
            movie_url = movie_json["poster"]
            caption = (f"{movie_json["name"]} ({voice} | {quality}p)\n\n"
                       f"⚠️ Видео еще не загружено, возможно озвучка серии еще не вышла, выбери другую\n\n"
                       f"by @YandexKinoBot")
    else:
        series = context.user_data["series"]
        all_series: list[str] = movie_json["all_series"]

        if all_series.index(series) == 0:
            prev_button = InlineKeyboardButton("✖️ Предыдущая", callback_data=NONE)
        else:
            prev_button = InlineKeyboardButton("⬅️ Предыдущая",
                                               callback_data=f"{SHOW} series {all_series[all_series.index(series) - 1]}")

        if all_series.index(series) == len(all_series) - 1:
            next_button = InlineKeyboardButton("✖️ Следующая", callback_data=NONE)
        else:
            next_button = InlineKeyboardButton("➡️ Следующая",
                                               callback_data=f"{SHOW} series {all_series[all_series.index(series) + 1]}")

        keyboard = [
            [prev_button, next_button],
            [InlineKeyboardButton("🔢 Выбор серии", callback_data=f"{SERIES} voice")],
            [
                InlineKeyboardButton("🔊 Озвучка", callback_data=VOICES),
                InlineKeyboardButton("🔮 Качество", callback_data=QUALITY)
            ],
            [InlineKeyboardButton("🔙 Назад", callback_data=NEW_SEARCH)]
        ]

        try:
            media_type = "video"
            movie_url = movie_json["videos"][series][voice][quality]
            caption = (f"{movie_json["name"]} ({voice} | {quality}p)\n" +
                       "сезон {} серия {}\n\n".format(*series.split('e')) +
                       f"by @YandexKinoBot")
        except KeyError:
            media_type = "photo"
            movie_url = movie_json["poster"]
            caption = (f"{movie_json["name"]} ({voice} | {quality}p)\n" +
                       "сезон {} серия {}\n\n".format(*series.split('e')) +
                       f"⚠️ Видео еще не загружено, возможно озвучка серии еще не вышла, выбери другую\n\n"
                       f"by @YandexKinoBot")

    await query.edit_message_media(InputMedia(media_type, movie_url))
    await query.edit_message_caption(caption)
    await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))


async def change_voices(update, context):
    """Выводит кнопки для выбора озвучки при callback=VOICES"""
    query = update.callback_query
    await query.answer()

    json_data = context.user_data["movie_json"]

    if json_data["type"] == 0:
        voices = list(json_data["videos"].keys())
    else:
        series = context.user_data["series"]
        voices = list(json_data["videos"][series].keys())

    keyboard = [[InlineKeyboardButton(voice, callback_data=f"{SHOW} voice {voice}")] for voice in voices]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=SHOW)])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))


async def change_quality(update, context):
    """Выводит кнопки для выбора качества при callback=QUALITY"""
    query = update.callback_query
    await query.answer()

    voice = context.user_data["voice"]
    json_data = context.user_data["movie_json"]

    if json_data["type"] == 0:
        qualities = list(json_data["videos"][voice].keys())
    else:
        series = context.user_data["series"]
        qualities = list(json_data["videos"][series][voice].keys())

    keyboard = [[InlineKeyboardButton(quality, callback_data=f"{SHOW} quality {quality}")] for quality in qualities]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=SHOW)])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))


async def change_series(update, context):
    """Выводит кнопки для выбора серии при callback=SERIES"""
    query = update.callback_query
    await query.answer()

    _, data = query.data.split()

    if data == "voice":
        keyboard = [
            [InlineKeyboardButton("✅ Серии озвучки", callback_data=f"{SERIES} voice"),
             InlineKeyboardButton("🔲 Все серии", callback_data=f"{SERIES} all")],
        ]

        series = [
            episode for episode in context.user_data["movie_json"]["all_series"]
            if context.user_data["voice"] in list(context.user_data["movie_json"]["videos"][episode].keys())
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🔲 Серии озвучки", callback_data=f"{SERIES} voice"),
             InlineKeyboardButton("✅ Все серии", callback_data=f"{SERIES} all")],
        ]

        series = context.user_data["movie_json"]["all_series"]

    series = list(map(lambda episode: InlineKeyboardButton(episode, callback_data=f"{SHOW} series {episode}"), series))
    if len(series) < len(context.user_data["movie_json"]["all_series"]):
        series.append(InlineKeyboardButton("🔢➡️", callback_data=f"{SERIES} all"))

    keyboard.extend([series[i:i + 4] for i in range(0, len(series), 4)])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=SHOW)])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))


def main():
    """Функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # задаёт выполнение функции start при команде /start
    application.add_handler(CommandHandler("start", start))
    # задаёт выполнение функции reply при получении текстового сообщения от пользователя
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    # задаёт выполнение функции search при нажатии кнопки содержавшую в callback SEARCH
    application.add_handler(CallbackQueryHandler(search, pattern=f"^{SEARCH}$"))
    # задаёт выполнение функции new_search при нажатии кнопки содержавшую в callback NEW_SEARCH
    application.add_handler(CallbackQueryHandler(new_search, pattern=f"^{NEW_SEARCH}$"))
    # задаёт выполнение функции instruction при нажатии кнопки содержавшую в callback INSTRUCTION
    application.add_handler(CallbackQueryHandler(instruction, pattern=f"^{INSTRUCTION}$"))
    # задаёт выполнение функции show_movie при нажатии кнопки содержавшую в callback SHOW
    application.add_handler(CallbackQueryHandler(show_movie, pattern=f"^{SHOW}.*$"))
    # задаёт выполнение функции change_voices при нажатии кнопки содержавшую в callback VOICES
    application.add_handler(CallbackQueryHandler(change_voices, pattern=f"^{VOICES}$"))
    # задаёт выполнение функции change_quality при нажатии кнопки содержавшую в callback QUALITY
    application.add_handler(CallbackQueryHandler(change_quality, pattern=f"^{QUALITY}$"))
    # задаёт выполнение функции change_series при нажатии кнопки содержавшую в callback SERIES
    application.add_handler(CallbackQueryHandler(change_series, pattern=f"^{SERIES}.*$"))

    application.run_polling()


if __name__ == '__main__':
    main()
