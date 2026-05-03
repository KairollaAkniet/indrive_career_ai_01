import requests
import os
import re
from dotenv import load_dotenv
import whisper
import aiohttp

async def save_to_dashboard(data):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8000/api/candidates/', json=data) as resp:
            return await resp.json()

model = whisper.load_model("base")


def convert_voice_to_text(file_path):
    """Распознавание голоса через Whisper"""
    try:
        result = model.transcribe(file_path, language="ru", task="transcribe", fp16=False)
        recognized_text = result["text"].strip()
        print(f"DEBUG Whisper распознал: {recognized_text}")
        return recognized_text
    except Exception as e:
        print(f"Ошибка Whisper: {e}")
        return None


load_dotenv()

API_KEY = os.getenv("INDRIVE_API_KEY")
URL = "https://llm.alem.ai/v1/chat/completions"
BACKEND_URL = "http://0.0.0.0:8000/api/bot-data"


def _call_llm(system_prompt: str, user_text: str, max_tokens: int = 800) -> str | None:
    """Внутренняя функция — отправляет запрос в alemllm API."""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "alemllm",
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
        }
        response = requests.post(URL, json=payload, headers=headers, timeout=45)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        print(f"Ошибка API: {response.status_code} — {response.text[:200]}")
        return None
    except Exception as e:
        print(f"Ошибка _call_llm: {e}")
        return None


def analyze_candidate_score(user_text: str):
    """
    Оценивает текст кандидата.
    Возвращает: (score: float, feedback: str, ai_probability: float)
    """
    system_prompt = """Ты опытный рекрутер компании inDrive.
Оцени текст кандидата.

Ответ СТРОГО в таком формате:
БАЛЛ: 0.75
СОВЕТ: (краткий совет на русском, 2-3 предложения)

Правила:
- БАЛЛ от 0.0 до 1.0
- СОВЕТ только на русском языке
- Больше ничего не пиши"""

    content = _call_llm(system_prompt, user_text)
    if not content:
        return 0.5, "Не удалось выполнить анализ. Попробуйте ещё раз.", 0.1

    score_match = re.search(r"БАЛЛ:\s*(\d+[\.,]\d+)", content)
    advice_match = re.search(r"СОВЕТ:\s*(.+)", content, re.DOTALL)

    score = float(score_match.group(1).replace(",", ".")) if score_match else 0.5
    score = max(0.0, min(1.0, score))
    feedback = advice_match.group(1).strip() if advice_match else content[:300]

    return score, feedback, 0.1


def detect_ai_or_human(text: str) -> dict:
    """
    Определяет — человек написал текст или ИИ.

    Возвращает:
    {
        "label":       "human" | "ai" | "mixed" | "unknown",
        "probability": float,   <- вероятность что написал ИИ (0.0–1.0)
        "explanation": str,     <- объяснение на русском
        "markers":     list     <- найденные признаки
    }
    """
    if not text or len(text.strip()) < 30:
        return {
            "label": "unknown",
            "probability": 0.0,
            "explanation": "Текст слишком короткий для анализа.",
            "markers": []
        }

    system_prompt = """Ты эксперт по анализу текстов. Определи — текст написал человек или искусственный интеллект.

Признаки текста написанного ИИ:
- Идеальная грамматика, нет ошибок и опечаток
- Шаблонные фразы: "во-первых", "таким образом", "в заключение", "следует отметить"
- Одинаковая длина предложений, монотонный ритм
- Нет личного опыта, эмоций, конкретных примеров из жизни
- Академический, "роботизированный" стиль
- Слишком полный и идеально структурированный ответ

Признаки текста написанного человеком:
- Грамматические или стилистические ошибки
- Личный опыт, конкретные детали и примеры
- Разная длина предложений, живой ритм
- Разговорные слова, эмоции
- Отступления от темы или неполные мысли
- Сокращения, неформальный стиль

Ответ СТРОГО в таком формате (ничего лишнего не пиши):

ТИП: human
ВЕРОЯТНОСТЬ: 0.15
ПРИЗНАКИ: есть ошибки, личный опыт, разговорный стиль
ОБЪЯСНЕНИЕ: В тексте есть грамматические ошибки и личный опыт, что указывает на человека.

ТИП может быть только: human / ai / mixed
ВЕРОЯТНОСТЬ — вероятность что текст написал ИИ, от 0.0 до 1.0"""

    content = _call_llm(system_prompt, text, max_tokens=400)

    if not content:
        return {
            "label": "unknown",
            "probability": 0.1,
            "explanation": "Не удалось выполнить анализ.",
            "markers": []
        }

    type_match = re.search(r"ТИП:\s*(human|ai|mixed)", content, re.IGNORECASE)
    prob_match = re.search(r"ВЕРОЯТНОСТЬ:\s*(\d+[\.,]\d+)", content)
    marks_match = re.search(r"ПРИЗНАКИ:\s*(.+)", content)
    expl_match = re.search(r"ОБЪЯСНЕНИЕ:\s*(.+)", content, re.DOTALL)

    label = type_match.group(1).lower() if type_match else "unknown"

    probability = 0.5
    if prob_match:
        probability = float(prob_match.group(1).replace(",", "."))
        probability = max(0.0, min(1.0, probability))

    markers = []
    if marks_match:
        markers = [m.strip() for m in marks_match.group(1).split(",") if m.strip()]

    explanation = expl_match.group(1).strip() if expl_match else content[:200]

    return {
        "label": label,
        "probability": probability,
        "explanation": explanation,
        "markers": markers
    }


def format_ai_detection_result(result: dict) -> str:
    """
    Форматирует результат detect_ai_or_human в красивое сообщение для Telegram.
    Все тексты на русском.
    """
    label = result.get("label", "unknown")
    prob = result.get("probability", 0.0)
    expl = result.get("explanation", "")
    marks = result.get("markers", [])

    label_info = {
        "human": ("👤", "Написал человек", "🟢"),
        "ai": ("🤖", "Написал ИИ", "🔴"),
        "mixed": ("⚠️", "Смешанный (человек + ИИ)", "🟡"),
        "unknown": ("❓", "Не определено", "⚪"),
    }
    icon, name, color = label_info.get(label, ("❓", "Не определено", "⚪"))

    # Прогресс-бар (10 символов)
    filled = round(prob * 10)
    bar = "█" * filled + "░" * (10 - filled)

    lines = [
        f"{icon} *Тип автора: {name}*",
        f"{color} Вероятность ИИ: `{bar}` {int(prob * 100)}%",
        "",
        f"📝 *Объяснение:*",
        expl,
    ]

    if marks:
        lines.append("")
        lines.append("🔍 *Найденные признаки:*")
        for m in marks[:4]:
            lines.append(f"  • {m}")

    return "\n".join(lines)


def analyze_full(user_text: str):
    """
    Полный анализ текста:
    1. Оценка кандидата — балл + совет
    2. Детекция ИИ / Человек

    Возвращает: (score, feedback, ai_probability, detection_result)
    """
    score, feedback, _ = analyze_candidate_score(user_text)
    detection = detect_ai_or_human(user_text)
    return score, feedback, detection["probability"], detection


def send_to_backend(user_id, username, full_name, text, score, summary):
    """Отправка данных в FastAPI бэкенд"""
    payload = {
        "user_id": user_id,
        "username": username or "unknown",
        "full_name": full_name,
        "answers_text": text,
        "ai_score": int(score * 100),
        "ai_summary": summary
    }
    try:
        requests.post(BACKEND_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Ошибка отправки на бэкенд: {e}")
