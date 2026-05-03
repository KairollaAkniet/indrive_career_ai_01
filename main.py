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
from aiogram.types import Message, BufferedInputFile
from dotenv import load_dotenv
import aiohttp

import requests


def send_to_dashboard(candidate_data):
    # Адрес твоего запущенного API
    url = "http://172.20.10.5:8000/api/candidates/"

    # Отправка данных
    response = requests.post(url, json=candidate_data)

    if response.status_code == 201:
        print("Данные успешно улетели на сайт!")
    else:
        print("Ошибка при отправке:", response.text)


async def save_to_dashboard(data):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://172.20.10.5:8000/api/candidates/', json=data) as resp:
            return await resp.json()

try:
    from indrive_api import analyze_full, convert_voice_to_text, format_ai_detection_result
except ImportError:
    logging.error("❌ Файл indrive_api.py не найден!")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_API = "http://172.20.10.5:8000/api/candidates/"
DASHBOARD_URL = "http://172.20.10.5:5173/"
DJANGO_API = "http://172.20.10.5:8000/api/candidates/"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)


# ─── База данных SQLite ───────────────────────────────────────────────
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


# ─── Состояния FSM
class Interview(StatesGroup):
    project = State()
    tech_stack = State()
    soft_skills = State()


class ReminderStates(StatesGroup):
    topic = State()
    delay = State()


# ─── Вспомогательные функции
def get_dashboard_markup():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🌐 Посмотреть результаты на сайте", url=DASHBOARD_URL
    ))
    return builder.as_markup()


def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🚀 Начать собеседование"))
    builder.row(types.KeyboardButton(text="📱 Показать меню"))
    builder.row(types.KeyboardButton(text="📊 Получить отчёт"))
    builder.row(types.KeyboardButton(text="🔔 Напоминание"))
    return builder.as_markup(resize_keyboard=True)


def inline_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🧠 Ментор (проверка знаний)", callback_data="mode_mentor"))
    builder.row(types.InlineKeyboardButton(text="💬 AI-советник", callback_data="mode_consultant"))
    builder.row(types.InlineKeyboardButton(text="🎤 Анализ аудио", callback_data="mode_audio"))
    builder.row(types.InlineKeyboardButton(text="📄 Проверить файл (.docx)", callback_data="mode_file"))
    builder.row(types.InlineKeyboardButton(text="📊 Dashboard (перейти)", url=DASHBOARD_URL))
    builder.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="mode_profile"))
    return builder.as_markup()


def safe_analyze(text: str):
    try:
        result = analyze_full(text)
        if isinstance(result, tuple) and len(result) == 4:
            return result
    except Exception as e:
        logging.error(f"Ошибка safe_analyze: {e}")
    return 0.5, "Ошибка анализа", 0.1, {
        "label": "unknown", "probability": 0.1,
        "explanation": "", "markers": []
    }


def send_to_dashboard(user_id, username, full_name, text, score, summary, prob=0.1, label="unknown"):
    try:
        payload = {
            "user_id": int(user_id),
            "username": str(username or "Unknown"),
            "full_name": str(full_name or "Anonymous"),
            "answers_text": str(text),
            "ai_score": int(score * 100) if score <= 1 else int(score),
            "ai_summary": str(summary),
            "ai_probability": int(prob * 100) if prob <= 1 else int(prob)
        }

        response = requests.post(BACKEND_API, json=payload, timeout=5)

        if response.status_code == 201:
            logging.info(f"Данные успешно ушли в Django для {full_name}")
        else:
            logging.error(f"Ошибка Django API: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"⚠Ошибка при связи с дашбордом: {e}")


def build_result_message(score: float, feedback: str, detection: dict) -> str:
    """Итоговое сообщение: балл + детекция ИИ/Человек."""
    score_pct = int(score * 100) if score <= 1 else int(score)
    if score_pct >= 80:
        score_icon = "🟢"
    elif score_pct >= 50:
        score_icon = "🟡"
    else:
        score_icon = "🔴"

    detection_text = format_ai_detection_result(detection)
    return (
        f"{score_icon} *Результат: {score_pct}%*\n"
        f"💡 {feedback}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{detection_text}"
    )


# ─── Обработчики

@router.message(Command("start"))
async def cmd_start(message: Message):
    update_user_info(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        "👋 Привет! Выберите нужный раздел в меню ниже:",
        reply_markup=main_menu()
    )


@router.message(F.text == "📱 Показать меню")
async def show_all_modes(message: Message):
    await message.answer("🛠 Выберите функцию:", reply_markup=inline_menu())


@router.callback_query(F.data.startswith("mode_"))
async def callbacks(c: types.CallbackQuery):
    mode = c.data.split("_")[1]
    if mode == "profile":
        await c.message.answer(
            f"👤 Профиль: {c.from_user.full_name}\n"
            f"🆔 ID: {c.from_user.id}"
        )
    else:
        update_user_mode_in_db(c.from_user.id, mode)
        mode_messages = {
            "mentor": "🧠 Режим Ментор включён. Напишите тему — я буду задавать вопросы.",
            "consultant": "💬 Режим AI-советник включён. Напишите текст для анализа.",
            "audio": "🎤 Режим анализа аудио включён. Отправьте голосовое сообщение.",
            "file": "📄 Режим проверки файла включён. Отправьте .docx файл.",
        }
        await c.message.answer(mode_messages.get(mode, f"✅ Режим включён: {mode.upper()}"))
    await c.answer()

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Я бот для отслеживания карьеры. Вот что я могу:\n/start - Регистрация\n/dashboard - Ссылка на сайт")

# ─── Собеседование

@router.message(F.text == "🚀 Начать собеседование")
async def start_interview(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("1/3: Расскажите о самом сложном проекте, в котором вы участвовали?")
    await state.set_state(Interview.project)


@router.message(Interview.project)
async def step2(message: Message, state: FSMContext):
    await state.update_data(p=message.text)
    await message.answer("2/3: Какой у вас технологический стек?")
    await state.set_state(Interview.tech_stack)


@router.message(Interview.tech_stack)
async def step3(message: Message, state: FSMContext):
    await state.update_data(t=message.text)
    await message.answer("3/3: Как вы решаете конфликты в команде?")
    await state.set_state(Interview.soft_skills)


@router.message(Interview.soft_skills)
async def final_step(message: Message, state: FSMContext):
    data = await state.get_data()
    full_txt = f"Проект: {data.get('p')}\nСтек: {data.get('t')}\nSoft skills: {message.text}"
    msg = await message.answer("⏳ AI анализирует ваши ответы...")
    s, f, p, detection = safe_analyze(full_txt)
    send_to_dashboard(
        message.from_user.id, message.from_user.username,
        message.from_user.full_name, full_txt, s, f, p, detection.get("label")
    )
    await msg.delete()
    await message.answer(
        build_result_message(s, f, detection),
        reply_markup=get_dashboard_markup(),
        parse_mode="Markdown"
    )
    await state.clear()


# ─── Аудио

@router.message(F.voice | F.audio)
async def audio_proc(message: Message):
    status = await message.answer("⏳ Обрабатываю аудио...")
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(file_id)
    path = f"temp_{file_id}.ogg"
    await bot.download_file(file.file_path, path)

    text = convert_voice_to_text(path)
    if text:
        s, f, p, detection = safe_analyze(text)
        send_to_dashboard(
            message.from_user.id, message.from_user.username,
            message.from_user.full_name, text, s, f, p, detection.get("label")
        )
        await status.edit_text(
            f"📝 *Распознанный текст:*\n{text[:300]}\n\n"
            + build_result_message(s, f, detection),
            reply_markup=get_dashboard_markup(),
            parse_mode="Markdown"
        )
    else:
        await status.edit_text("❌ Не удалось распознать аудио. Попробуйте ещё раз.")

    if os.path.exists(path):
        os.remove(path)


# ─── Файл .docx

@router.message(F.document)
async def file_proc(message: Message):
    if not message.document.file_name.endswith('.docx'):
        return await message.answer("⚠️ Пожалуйста, отправьте файл в формате .docx")

    status = await message.answer("⏳ Читаю и анализирую файл...")
    file = await bot.get_file(message.document.file_id)
    path = f"temp_{message.document.file_name}"
    await bot.download_file(file.file_path, path)

    doc = Document(path)
    full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    if not full_text.strip():
        await status.edit_text("❌ В файле не найден текст.")
        if os.path.exists(path):
            os.remove(path)
        return

    s, f, p, detection = safe_analyze(full_text)
    send_to_dashboard(
        message.from_user.id, message.from_user.username,
        message.from_user.full_name, full_text, s, f, p, detection.get("label")
    )
    await status.edit_text(
        "📄 *Файл проанализирован!*\n\n" + build_result_message(s, f, detection),
        reply_markup=get_dashboard_markup(),
        parse_mode="Markdown"
    )
    if os.path.exists(path):
        os.remove(path)


# ─── /report — Excel отчёт ────────────────────────────────────────────

@router.message(Command("report"))
@router.message(F.text == "📊 Получить отчёт")
async def cmd_report(message: Message):
    status = await message.answer("⏳ Формирую Excel отчёт...")
    try:
        response = requests.get(f"{DJANGO_API}/report/{message.from_user.id}/", timeout=30)
        if response.status_code == 200:
            excel_file = BufferedInputFile(response.content, filename="candidates_report.xlsx")
            await message.answer_document(
                excel_file,
                caption="📊 Отчёт по всем кандидатам готов!\n✅ Excel файл сформирован."
            )
            await status.delete()
        else:
            await status.edit_text("❌ Ошибка при формировании отчёта. Попробуйте позже.")
    except requests.exceptions.ConnectionError:
        await status.edit_text(
            "❌ Сервер Django недоступен.\n"
            "Убедитесь, что он запущен: python manage.py runserver 8001"
        )
    except Exception as e:
        await status.edit_text(f"❌ Ошибка: {str(e)[:100]}")


# ─── /remind — Напоминания ────────────────────────────────────────────

@router.message(Command("remind"))
@router.message(F.text == "🔔 Напоминание")
async def cmd_remind(message: Message, state: FSMContext):
    await message.answer(
        "📚 *Создание напоминания*\n\n"
        "По какой теме вам напомнить? Напишите тему:",
        parse_mode="Markdown"
    )
    await state.set_state(ReminderStates.topic)


@router.message(ReminderStates.topic)
async def remind_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="⏰ Через 24 часа", callback_data="remind_1"),
        types.InlineKeyboardButton(text="📅 Через 2 минуты", callback_data="remind_2"),
        types.InlineKeyboardButton(text="🗓 Через 7 дней", callback_data="remind_7"),
    )
    await message.answer(
        f"✅ Тема: *{message.text}*\n\nКогда напомнить?",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await state.set_state(ReminderStates.delay)


@router.callback_query(F.data.startswith("remind_"))
async def remind_delay(c: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    topic = data.get("topic", "Без темы")


    selection = c.data.split("_")[1]
    if selection == "1":
        seconds = 86400
        label = "24 часа"
    elif selection == "2":
        seconds = 120
        label = "2 минуты"
    else:
        seconds = 604800
        label = "7 дней"

    await c.message.edit_text(f"✅ Напоминание установлено!\nТема: {topic}\nЯ напомню через {label}.")


    async def send_later(wait_sec, chat_id, text):
        await asyncio.sleep(wait_sec)
        await bot.send_message(chat_id, f"🔔 НАПОМИНАНИЕ!\nВы просили напомнить про: {text}")

    asyncio.create_task(send_later(seconds, c.from_user.id, topic))

    await state.clear()
    await c.answer()

# ─── Свободный текст ─────────────────────────────────────────────────

@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    ignore_list = [
        "🚀 Начать собеседование", "🚀 Сұхбатты бастау",
        "📱 Показать меню", "📱 Көрсету меню",
        "📊 Получить отчёт", "📊 Есеп алу",
        "🔔 Напоминание", "🔔 Еске салу",
        "/help", "/start"
    ]

    if await state.get_state() or message.text in ignore_list:
        return
    mode = get_user_mode(message.from_user.id)

    mode = get_user_mode(message.from_user.id)
    status = await message.answer("⏳ Анализирую...")

    if mode == "mentor":
        prompt = (
            f"Ты технический ментор. Пользователь написал: '{message.text}'. "
            "НЕ пиши анализ или советы. "
            "Задай ТОЛЬКО 1 конкретный технический вопрос для проверки знаний."
        )
        s, question, p, detection = safe_analyze(prompt)
        send_to_dashboard(
            message.from_user.id, message.from_user.username,
            message.from_user.full_name, message.text, s, question, p
        )
        await status.edit_text(f"🧠 {question}", reply_markup=get_dashboard_markup())
    else:
        s, feedback, p, detection = safe_analyze(message.text)
        send_to_dashboard(
            message.from_user.id, message.from_user.username,
            message.from_user.full_name, message.text, s, feedback, p, detection.get("label")
        )
        await status.edit_text(
            build_result_message(s, feedback, detection),
            reply_markup=get_dashboard_markup(),
            parse_mode="Markdown"
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
