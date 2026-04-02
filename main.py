import asyncio
import os
import logging
import random
import requests
import docx
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from dotenv import load_dotenv

# Өзіңнің файлдарың мен База импорты
from indrive_api import analyze_candidate_score, convert_voice_to_text
from database import init_db, update_user_info, get_user_mode, save_result

# 1. БАПТАУЛАР
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Dashboard-тың IP-і мен порты (Ақниет, осыны тексер!)
# main.py ішінде:
# main.py басында:
YOUR_IP = "192.168.10.88" # Өз IP-іңді жаз (ipconfig-тен алған)

DASHBOARD_URL = f"http://192.168.10.88:5173/"
BACKEND_API = f"http://192.168.10.88:8000/api/bot-data"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

init_db()  # Базаны қосу

CHALLENGES = [
    "Challenge: Python-да 'list comprehension' қалай жұмыс істейді? Мысал келтір.",
    "Challenge: Solana блокчейнінде 'Smart Contract' орнына не қолданылады?",
    "Challenge: React-те 'Virtual DOM' не үшін керек?",
    "Challenge: SQL-де 'JOIN' түрлерін түсіндіріп бер.",
    "Challenge: AQUA-STEM жобаңда деректерді қалай сақтайсың?"
]


# 2. МӘЗІРЛЕР (KEYBOARDS)
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📱 Показать меню"))
    return builder.as_markup(resize_keyboard=True)


def inline_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🧠 Mentor (Тексеру)", callback_data="mode_mentor"))
    builder.row(types.InlineKeyboardButton(text="💬 AI Кеңесші", callback_data="mode_consultant"))
    builder.row(types.InlineKeyboardButton(text="🎤 Аудио-талдау", callback_data="mode_audio"))
    builder.row(types.InlineKeyboardButton(text="📄 Файл тексеру (.docx)", callback_data="mode_file"))
    # ӘРҚАШАН ТҰРАТЫН СІЛТЕМЕ
    builder.row(types.InlineKeyboardButton(text="📊 Dashboard (Сайтқа өту)", url=DASHBOARD_URL))
    builder.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="mode_profile"))
    return builder.as_markup()


def get_dashboard_button():
    """Әр жауаптан кейін шығатын батырма"""
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📊 Толық нәтижені сайттан көру", url=DASHBOARD_URL))
    return builder.as_markup()


# 3. ХЕНДЛЕРЛЕР
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    update_user_info(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(f"Сәлем, {message.from_user.first_name}! 🚀\nМен InDrive AI ассистентімін.",
                         reply_markup=main_menu())


@dp.message(F.text == "📱 Показать меню")
async def show_categories(message: types.Message):
    await message.answer("🛠 Керекті функцияны таңдаңыз:", reply_markup=inline_menu())


@dp.callback_query(F.data.startswith("mode_"))
async def select_mode(callback: types.CallbackQuery):
    mode = callback.data.split("_")[1]
    user_id = callback.from_user.id

    if mode == "profile":
        import sqlite3
        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()
        cursor.execute('SELECT last_score, total_tasks FROM users WHERE user_id = ?', (user_id,))
        data = cursor.fetchone()
        conn.close()
        score = data[0] if data else 0.0
        tasks = data[1] if data else 0
        await callback.message.answer(
            f"👤 Профиль: {callback.from_user.full_name}\n📊 Соңғы балл: {score}\n✅ Жұмыстар: {tasks}\n🎓 Оқу орны: AUES",
            reply_markup=get_dashboard_button())
    else:
        update_user_mode_in_db(user_id, mode)
        msg = {
            "mentor": f"🧠 AI Тапсырмасы:\n{random.choice(CHALLENGES)}\n\nЖауабыңызды жазыңыз.",
            "consultant": "💬 Мен сенің Full Stack менторыңмын. Сұрағыңды қой.",
            "audio": "🎤 Аудио-хабарлама жіберіңіз, мен оны талдаймын.",
            "file": "📄 .docx файлын жіберіңіз (Lab жұмысы)."
        }
        await callback.message.answer(msg.get(mode, "Режим таңдалды."), reply_markup=get_dashboard_button())
    await callback.answer()


def update_user_mode_in_db(user_id, mode):
    import sqlite3
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET current_mode = ? WHERE user_id = ?', (mode, user_id))
    conn.commit()
    conn.close()


# Мәтінді өңдеу
@dp.message(F.text & ~F.status_updates)
async def handle_text(message: types.Message):
    if message.text == "📱 Показать меню": return
    user_id = message.from_user.id
    mode = get_user_mode(user_id)

    status_msg = await message.answer("⏳ AI ойланып жатыр...")
    score, feedback = analyze_candidate_score(message.text)

    if mode == "mentor":
        save_result(user_id, message.text, score, feedback)
        send_to_dashboard(user_id, message.from_user.username, message.from_user.full_name, message.text, score,
                          feedback)
        await status_msg.edit_text(f"📊 Баға: {score}\n💡 AI: {feedback}", reply_markup=get_dashboard_button())
    else:
        await status_msg.edit_text(f"🤖 Кеңес:\n{feedback}", reply_markup=get_dashboard_button())


# Аудио
@dp.message(F.voice)
async def handle_voice(message: types.Message):
    user_id = message.from_user.id
    if get_user_mode(user_id) != "audio":
        return await message.answer("⚠️ Алдымен 'Аудио' режимін таңдаңыз.")

    status_msg = await message.answer("🎤 Дауысты танып жатырмын...")
    file = await bot.get_file(message.voice.file_id)
    path = f"{message.voice.file_id}.ogg"
    await bot.download_file(file.file_path, path)

    text = convert_voice_to_text(path)
    if text:
        score, feedback = analyze_candidate_score(text)
        save_result(user_id, text, score, feedback)
        await status_msg.edit_text(f"📝 Текст: {text}\n📊 Баға: {score}\n💡 AI: {feedback}",
                                   reply_markup=get_dashboard_button())
    else:
        await status_msg.edit_text("❌ Дауысты тану мүмкін болмады.")
    if os.path.exists(path): os.remove(path)


# Файл
@dp.message(F.document)
async def handle_docx(message: types.Message):
    user_id = message.from_user.id
    if get_user_mode(user_id) != "file":
        return await message.answer("⚠️ Алдымен 'Файл' режимін таңдаңыз.")

    if message.document.file_name.endswith('.docx'):
        status_msg = await message.answer("📄 Файлды оқып жатырмын...")
        file = await bot.get_file(message.document.file_id)
        path = f"downloads/{message.document.file_name}"
        if not os.path.exists("downloads"): os.makedirs("downloads")
        await bot.download_file(file.file_path, path)

        doc = docx.Document(path)
        content = "\n".join([p.text for p in doc.paragraphs])
        score, feedback = analyze_candidate_score(content)
        save_result(user_id, f"Файл: {message.document.file_name}", score, feedback)
        await status_msg.edit_text(f"📊 Баға: {score}\n💡 Талдау: {feedback}", reply_markup=get_dashboard_button())
    else:
        await message.answer("❌ Тек .docx файлын жіберіңіз.")


# Dashboard-қа жіберу
def send_to_dashboard(user_id, username, full_name, text, score, summary):
    payload = {
        "user_id": user_id, "username": username or "Akniet",
        "full_name": full_name or "Akniet", "answers_text": text,
        "ai_score": int(score * 100), "ai_summary": summary
    }
    try:
        requests.post(BACKEND_API, json=payload, timeout=5)
    except:
        logging.error("Dashboard байланыс қатесі")


# Іске қосу
async def main():
    print("🚀 Бот іске қосылды (Full Link Menu)!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())