import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# Твой файл с логикой ИИ
from indrive_api import analyze_candidate_score

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветствие пользователя"""
    welcome_text = (
        f"Привет, {message.from_user.first_name}! \n\n"
        "Я AI-ассистент программы **inVision U** от inDrive.\n"
        "Чтобы оценить твой потенциал, расскажи немного о себе: "
        "какие проекты ты делал, что знаешь в IT и почему хочешь к нам?"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(F.text)
async def handle_analysis(message: types.Message):
    """Обработка текста и вызов AlemLLM / Scoring API"""
    # Отправляем временное сообщение, чтобы пользователь не скучал
    status_msg = await message.answer("⏳ Мой ИИ анализирует твой ответ... Подожди немного.")

    # Вызываем функцию из твоего файла indrive_api.py
    score, feedback = analyze_candidate_score(message.text)

    # Удаляем временное сообщение
    await status_msg.delete()

    # Логика вердикта и текста кнопки
    if score >= 0.7:
        verdict = "🚀 **Рекомендован к зачислению!**"
        button_text = "Завершить регистрацию на сайте"
    elif score >= 0.4:
        verdict = "⚡ **Хороший потенциал (Лист ожидания)**"
        button_text = "Узнать подробности на сайте"
    else:
        verdict = "⚠️ **Нужно подтянуть знания**"
        button_text = "Посмотреть программу на сайте"

    # Формируем текст ответа (СНАЧАЛА СОЗДАЕМ, ПОТОМ ОТПРАВЛЯЕМ)
    final_response = (
        f"📊 **Твой Score:** `{score}`\n"
        f"✅ **Вердикт:** {verdict}\n\n"
        f"🤖 **Анализ ИИ:** {feedback}\n\n"
        "Нажми на кнопку ниже, чтобы продолжить на нашей платформе:"
    )

    # Вставь сюда тот адрес, который появился в строке Network (например 192.168.1.5)
    base_url = "http://172.20.10.5:5173/"  # ЗАМЕНИ НА СВОЙ ИЗ ТЕРМИНАЛА!

    full_url = f"{base_url}/?user_id={message.from_user.id}&score={score}&name={message.from_user.first_name}"

    # 3. Создаем кнопку с этой ссылкой
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text=button_text,
        url=full_url
    ))

    # 4. Отправляем итоговое сообщение с кнопкой
    await message.answer(
        final_response,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

async def main():
    logging.info("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот остановлен!")