import os
import asyncio
import platform
import random
import shutil
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import (
    FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton
)
import yt_dlp

# 🔹 Токен бота
import os
TOKEN = os.getenv("TOKEN")

# 🔹 Папка для загрузки музыки
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🔹 Путь к FFmpeg
FFMPEG_PATH = r"C:\Users\urfan\Desktop\ffmpeg-7.1.1-essentials_build\bin"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔹 Настройки yt_dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'ffmpeg_location': FFMPEG_PATH,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
}

# 🔹 Словари для пользователей
user_playlists = {}
user_languages = {}  # user_id: "ru" или "en"
user_search_results = {}  # user_id: list of search results

# 🔹 Словари для callback
download_map = {}
add_map = {}
id_counter = 0

# 🔹 GIF-анимации
DANCE_GIFS = [
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExam82bDZndzk4b2FjeDlkdnhwdjVpbThmYzQ0ZnI0OGFoa2gybHF4cyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LLHkw7UnvY3Kw/giphy.gif",
    "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWRnOGs0YnVmNzh5OWEzM2pleTY4Mjl5MnBmOHZxbjA3eTFnZXkyayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/tHIRLHtNwxpjIFqPdV/giphy.gif",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExejVmYmlwMTZ0aDV3dzN5N2JmMW54ZWJ6YmhuOG9oOTBqNzJtbjFhcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/DhstvI3zZ598Nb1rFf/giphy.gif",
    "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDdrZXRna2IwYzJqaTh1ZWJ1OGZyZjRsODlsa2ZoOXQ0aWJjN3ZvZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/KPgOYtIRnFOOk/giphy.gif",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExam82bDZndzk4b2FjeDlkdnhwdjVpbThmYzQ0ZnI0OGFoa2gybHF4cyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LLHkw7UnvY3Kw/giphy.gif",
    "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTY1eHcxOWg4ZTRyN3U0MjU2NGZwZWJzcGE2eHh3M2ZlNHN4ZXE4NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VNxwybK7VrJmzz4ZEI/giphy.gif",
    "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExYThsbnpnem9qOHhhdm53dHN3NHlnZXk3MDJ2eWdxZXl1dWQ1YXNwZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/nDSlfqf0gn5g4/giphy.gif",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2lwNHRqNWx4bTc1a3lwNWRyaGN1bW1xNmp6bXRiZHFxYnF4cm1lcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/DqhwoR9RHm3EA/giphy.gif",
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzNzcnhrdjR2bm9tbnRvaXQ2d2hjY3R3aHlvaHM3aDY1anFuZzY4NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZYoFTHxrWNFbW/giphy.gif",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExY2RuYTZsanU2NWl2OW95dWdnbmpvYTBxZWxjOHp4cHh0MjRieHAyeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/THlB4bsoSA0Cc/giphy.gif",
    "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYzJ2cXdubzFtbWEzcDB2ZHM1eXQzNm16eWs0NHZvN3VrOG5vaHFhYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3ohhwfAa9rbXaZe86c/giphy.gif",
    "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWI4OHp4bG90dThrZ3k1dG10OHYxNXlnNTU3NWFlYzJzNWZydzlhbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l41m3YpztVBtugahW/giphy.gif",
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnFtMWk0dG5hb2h3aTUxMHd2YTl6cjZhY29nYXFvZ2ZzNHQ1dHZsbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/10AmJ6TIlbYxAk/giphy.gif",
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGF3MzRhZjQxamdoOWp5M2s4N2l0aWRxMHZpODNibHZyMTJnZXBhdSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/8FM1f72L6sqB26NIsB/giphy.gif",
    "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExdTJsOHNwNGlqanowN2V3eXRqYWViaTlnaGljdHVsaHF2NXVqNWU0eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YbXtbKoi2ZUOc/giphy.gif",
    "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3d2ZXloa2QybDBjcHY5dDV0dnIxNWlpenR4a2JucHAzMmxyNW5wbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oAt1NiCiTCZrlZvy0/giphy.gif",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjVrODZtamp3bmphaGhzZ3BmMXlpOG9kMGF5NDlqOXpkYnc2dnhkNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/WXB88TeARFVvi/giphy.gif",
    "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWhsNnAyOGk0dnNsNTRtOTZ0dzE3cWM5bmU3aWNjaWRhbTZ2bjBpayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Y4WDXbagwPoepikUdJ/giphy.gif",
    "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHQ2amo2ZWVsbTh6aDh1NzJiNHhrb2h0OHFkcmU2a2d5Z2UwMDl6ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/RguvAFpdvkVzO/giphy.gif",
]

# 🔹 Сообщения на 2 языках
MESSAGES = {
    "start": {
        "ru": "Привет! Выбери язык, на котором бот будет с тобой общаться:",
        "en": "Hello! Choose the language for the bot:"
    },
    "menu": {
        "ru": "🎵 Отправь название песни или выбери действие:",
        "en": "🎵 Send a song name or choose an action:"
    },
    "playlist_empty": {
        "ru": "Твой плейлист пуст.",
        "en": "Your playlist is empty."
    },
    "playlist_cleared": {
        "ru": "Плейлист очищен.",
        "en": "Playlist cleared."
    },
    "searching": {
        "ru": "🔎 Ищу: {} ...",
        "en": "🔎 Searching for: {} ..."
    },
    "choose_song": {
        "ru": "Выбери песню:",
        "en": "Choose a song:"
    },
    "downloaded": {
        "ru": "Вот твоя песня:",
        "en": "Here is your song:"
    },
    "added": {
        "ru": "Добавлено в плейлист!",
        "en": "Added to playlist!"
    },
    "exists": {
        "ru": "Уже в плейлисте!",
        "en": "Already in playlist!"
    },
}


# 🔹 Главное меню
def main_menu(lang="ru"):
    if lang == "ru":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎵 Плейлист"), KeyboardButton(text="🗑 Очистить плейлист")],
                [KeyboardButton(text="ℹ️ Помощь")]
            ], resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎵 Playlist"), KeyboardButton(text="🗑 Clear playlist")],
                [KeyboardButton(text="ℹ️ Help")]
            ], resize_keyboard=True
        )


# 🔹 Кнопки выбора языка
def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])


# 🔹 Кнопки для песни
def make_song_buttons(mp3_path: str, title: str):
    global id_counter
    id_counter += 1
    download_id = f"d{id_counter}"
    id_counter += 1
    add_id = f"a{id_counter}"
    download_map[download_id] = mp3_path
    add_map[add_id] = title

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬇ Скачать", callback_data=download_id),
            InlineKeyboardButton(text="➕ В плейлист", callback_data=add_id),
            InlineKeyboardButton(text="🔗 Поделиться", switch_inline_query=title)
        ]
    ])
    return kb


# 🔹 /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(MESSAGES["start"]["ru"], reply_markup=language_keyboard())


# 🔹 Обработка выбора языка
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback_query: types.CallbackQuery):
    lang = callback_query.data.split("_")[1]
    user_languages[callback_query.from_user.id] = lang
    await callback_query.message.answer(
        MESSAGES["menu"][lang],
        reply_markup=main_menu(lang)
    )


# 🔹 Обработка текста (поиск песен)
@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "ru")
    text = message.text.lower()

    # Плейлист
    if text in ["🎵 плейлист", "🎵 playlist"]:
        pl = user_playlists.get(user_id, [])
        if not pl:
            await message.answer(MESSAGES["playlist_empty"][lang])
        else:
            await message.answer("\n".join(f"{i+1}. {p}" for i, p in enumerate(pl)))
        return

    # Очистка
    if text in ["🗑 очистить плейлист", "🗑 clear playlist"]:
        user_playlists[user_id] = []
        await message.answer(MESSAGES["playlist_cleared"][lang])
        return

    # Помощь
    if text in ["ℹ️ помощь", "ℹ️ help"]:
        await message.answer(MESSAGES["menu"][lang])
        return

    # Поиск песен
    await message.answer(MESSAGES["searching"][lang].format(message.text))

    loop = asyncio.get_event_loop()

    def run_yt_dlp():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{message.text}", download=False)
            return info['entries']

    try:
        results = await loop.run_in_executor(None, run_yt_dlp)
        if not results:
            await message.answer("❌ Нет результатов")
            return

        # Сохраняем результаты поиска для пользователя
        user_search_results[user_id] = results

        # Отправляем кнопки с песнями
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{i+1}. {r['title']} - {r.get('uploader','')}", callback_data=f"song_{i}")]
                for i, r in enumerate(results)
            ]
        )
        await message.answer(MESSAGES["choose_song"][lang], reply_markup=kb)

    except Exception as e:
        await message.answer(f"❌ Ошибка при поиске: {e}")


# 🔹 Выбор песни
@dp.callback_query(F.data.startswith("song_"))
async def choose_song(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = user_languages.get(user_id, "ru")

    results = user_search_results.get(user_id, [])
    idx = int(callback_query.data.split("_")[1])
    if idx >= len(results):
        await callback_query.answer("❌ Ошибка выбора")
        return

    song = results[idx]

    # Скачиваем песню
    loop = asyncio.get_event_loop()

    def download_song():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song['webpage_url'], download=True)
            filename = ydl.prepare_filename(info)
            mp3_file = filename.rsplit('.', 1)[0] + '.mp3'
            return mp3_file, info

    try:
        mp3_path, info = await loop.run_in_executor(None, download_song)
        audio = FSInputFile(mp3_path)
        title = info.get('title', 'Song')

        kb = make_song_buttons(mp3_path, title)
        await callback_query.message.answer_audio(
            audio=audio, caption=MESSAGES["downloaded"][lang], reply_markup=kb
        )
        await callback_query.message.answer_animation(random.choice(DANCE_GIFS))

        # Инициализация плейлиста
        user_playlists.setdefault(user_id, [])

    except Exception as e:
        await callback_query.message.answer(f"❌ Ошибка при скачивании: {e}")

    finally:
        # Автоочистка папки
        try:
            shutil.rmtree(DOWNLOAD_FOLDER)
            os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        except:
            pass


# 🔹 Обработка кнопок скачивания и добавления в плейлист
@dp.callback_query()
async def callback_buttons(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    lang = user_languages.get(user_id, "ru")

    if data in add_map:
        title = add_map[data]
        pl = user_playlists.setdefault(user_id, [])
        if title not in pl:
            pl.append(title)
            await callback_query.answer(MESSAGES["added"][lang])
        else:
            await callback_query.answer(MESSAGES["exists"][lang])
        return

    if data in download_map:
        path = download_map[data]
        if os.path.exists(path):
            audio = FSInputFile(path)
            await callback_query.message.answer_audio(audio=audio)
            await callback_query.answer()
        else:
            await callback_query.answer("❌ Файл не найден", show_alert=True)
        return


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
