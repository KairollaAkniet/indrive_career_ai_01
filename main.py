import asyncio
import os
import logging
import requests
import sqlite3
from docx import Document
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
try:
    from indrive_api import analyze_candidate_score, convert_voice_to_text
except ImportError:
    logging.error("❌ indrive_api.py файлы табылмады!")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_API = "http://192.168.8.230:8000/api/bot-data"
DASHBOARD_URL = "http://192.168.8.230:5173"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

def init_db():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, 
                       current_mode TEXT DEFAULT 'consultant')''')
    conn.commit()
    conn.close()

def update_user_info(user_id, username, full_name):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
                   (user_id, username, full_name))
    conn.commit()
    conn.close()

def update_user_mode_in_db(user_id, mode):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET current_mode = ? WHERE user_id = ?', (mode, user_id))
    conn.commit()
    conn.close()

def get_user_mode(user_id):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute('SELECT current_mode FROM users WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data[0] if data else "consultant"
init_db()

class Interview(StatesGroup):
    project = State()
    tech_stack = State()
    soft_skills = State()

def get_dashboard_markup():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🌐 Нәтижелерді сайттан көру", url=DASHBOARD_URL))
    return builder.as_markup()

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🚀 Сұхбатты бастау"))
    builder.row(types.KeyboardButton(text="📱 Көрсету меню"))
    return builder.as_markup(resize_keyboard=True)

def inline_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🧠 Mentor (Тексеру)", callback_data="mode_mentor"))
    builder.row(types.InlineKeyboardButton(text="💬 AI Кеңесші", callback_data="mode_consultant"))
    builder.row(types.InlineKeyboardButton(text="🎤 Аудио-талдау", callback_data="mode_audio"))
    builder.row(types.InlineKeyboardButton(text="📄 Файл тексеру (.docx)", callback_data="mode_file"))
    builder.row(types.InlineKeyboardButton(text="📊 Dashboard (Сайтқа өту)", url=DASHBOARD_URL))
    builder.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="mode_profile"))
    return builder.as_markup()

def safe_analyze(text):
    try:
        ans = analyze_candidate_score(text)
        if isinstance(ans, tuple) and len(ans) >= 2:
            return ans[0], ans[1], (ans[2] if len(ans) > 2 else 0.1)
    except:
        pass
    return 0.5, "Талдау қатесі", 0.1

def send_to_dashboard(user_id, username, full_name, text, score, summary, prob):
    try:
        payload = {
            "user_id": int(user_id), "username": str(username or "Unknown"),
            "full_name": str(full_name or "Anonymous"), "answers_text": str(text),
            "ai_score": int(score * 100) if score <= 1 else int(score),
            "ai_summary": str(summary), "ai_probability": int(prob * 100)
        }
        requests.post(BACKEND_API, json=payload, timeout=5)
    except:
        pass

@router.message(Command("start"))
async def cmd_start(message: Message):
    update_user_info(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer("Сәлем! Төмендегі менюден керекті бөлімді таңдаңыз 👇", reply_markup=main_menu())

@router.message(F.text == "📱 Көрсету меню")
async def show_all_modes(message: Message):
    await message.answer("🛠 Керекті функцияны таңдаңыз:", reply_markup=inline_menu())

@router.callback_query(F.data.startswith("mode_"))
async def callbacks(c: types.CallbackQuery):
    mode = c.data.split("_")[1]
    if mode == "profile":
        await c.message.answer(f"👤 Профиль: {c.from_user.full_name}\nID: {c.from_user.id}")
    else:
        update_user_mode_in_db(c.from_user.id, mode)
        if mode == "mentor":
            await c.message.answer("🧠 Mentor режимі қосылды. Тақырыпты жазыңыз, мен тек сұрақ қоямын.")
        else:
            await c.message.answer(f"✅ Режим қосылды: {mode.upper()}")
    await c.answer()

@router.message(F.text == "🚀 Сұхбатты бастау")
async def start_interview(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("1/3: Қатысқан ең күрделі жобаңыз туралы айтыңыз?")
    await state.set_state(Interview.project)

@router.message(Interview.project)
async def step2(message: Message, state: FSMContext):
    await state.update_data(p=message.text)
    await message.answer("2/3: Технологиялық стегіңіз?")
    await state.set_state(Interview.tech_stack)

@router.message(Interview.tech_stack)
async def step3(message: Message, state: FSMContext):
    await state.update_data(t=message.text)
    await message.answer("3/3: Командадағы конфликтті қалай шешесіз?")
    await state.set_state(Interview.soft_skills)

@router.message(Interview.soft_skills)
async def final_step(message: Message, state: FSMContext):
    data = await state.get_data()
    full_txt = f"Жоба: {data.get('p')}\nСтек: {data.get('t')}\nSoft: {message.text}"
    msg = await message.answer("⏳ AI талдап жатыр...")
    s, f, p = safe_analyze(full_txt)
    send_to_dashboard(message.from_user.id, message.from_user.username, message.from_user.full_name, full_txt, s, f, p)
    await msg.delete()
    await message.answer(f"✅ Аяқталды!\n📊 Баға: {int(s * 100)}%\n💡 AI: {f}", reply_markup=get_dashboard_markup())
    await state.clear()

@router.message(F.voice | F.audio)
async def audio_proc(message: Message):
    status = await message.answer("⏳ Аудио талдануда...")
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(file_id)
    path = f"temp_{file_id}.ogg"
    await bot.download_file(file.file_path, path)
    text = convert_voice_to_text(path)
    if text != "Қате":
        s, f, p = safe_analyze(text)
        send_to_dashboard(message.from_user.id, message.from_user.username, message.from_user.full_name, text, s, f, p)
        await status.edit_text(f"📝 Текст: {text}\n📊 Баға: {s}\n💡 AI: {f}", reply_markup=get_dashboard_markup())
    else:
        await status.edit_text("❌ Аудионы тану мүмкін болмады.")
    if os.path.exists(path): os.remove(path)

@router.message(F.document)
async def file_proc(message: Message):
    if not message.document.file_name.endswith('.docx'):
        return await message.answer("⚠️ Тек .docx файлын жіберіңіз.")
    status = await message.answer("⏳ Файл оқылуда...")
    file = await bot.get_file(message.document.file_id)
    path = f"temp_{message.document.file_name}"
    await bot.download_file(file.file_path, path)
    doc = Document(path)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    s, f, p = safe_analyze(full_text)
    send_to_dashboard(message.from_user.id, message.from_user.username, message.from_user.full_name, full_text, s, f, p)
    await status.edit_text(f"📄 Файл талданды!\n📊 Баға: {s}\n💡 AI: {f}", reply_markup=get_dashboard_markup())
    if os.path.exists(path): os.remove(path)

@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    if await state.get_state() or message.text in ["🚀 Сұхбатты бастау", "📱 Көрсету меню"]: return

    mode = get_user_mode(message.from_user.id)

    if mode == "mentor":
        prompt = (
            f"Сен техникалық Mentor-сың. Пайдаланушы мына тақырыпты таңдады немесе жауап берді: '{message.text}'. "
            "ЕШҚАНДАЙ үшінші жақтан талдау немесе кеңес жазба. "
            "ТЕК ҚАНА пайдаланушының білімін тексеретін 1 нақты техникалық сұрақ қой."
        )
        s, question, p = safe_analyze(prompt)
        send_to_dashboard(message.from_user.id, message.from_user.username, message.from_user.full_name, message.text,
                          s, question, p)
        await message.answer(f"🧠 {question}", reply_markup=get_dashboard_markup())
    else:
        s, feedback, p = safe_analyze(message.text)
        await message.answer(f"🤖 AI: {feedback}", reply_markup=get_dashboard_markup())

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())