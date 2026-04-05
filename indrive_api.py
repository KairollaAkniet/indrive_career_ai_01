import requests
import os
import re
from dotenv import load_dotenv
import whisper
import os

# Модельді жүктейміз (бірінші рет қосқанда сәл уақыт алуы мүмкін)
model = whisper.load_model("base")


def convert_voice_to_text(file_path):
    """Whisper-ді қазақ/орыс тіліне баптау"""
    try:
        # language="ru" немесе "kk" деп көрсету Whisper-ді адастырмайды
        # Егер орысша сөйлесең "ru", қазақша болса "kk" қой
        result = model.transcribe(file_path, language="ru", task="transcribe", fp16=False)

        recognized_text = result["text"].strip()
        print(f"DEBUG: Whisper таныған мәтін: {recognized_text}")  # Терминалдан тексеру үшін
        return recognized_text
    except Exception as e:
        print(f"Whisper қатесі: {e}")
        return None
load_dotenv()

API_KEY = os.getenv("INDRIVE_API_KEY")
URL = "https://llm.alem.ai/v1/chat/completions"
# СЕНІҢ FastAPI БЭКЕНДІҢНІҢ АДРЕСІ:
BACKEND_URL = "http://0.0.0.0:8000/api/bot-data"


def analyze_interview_answer(question, user_answer):
    """Сұхбат жауабын терең талдау"""
    prompt = f"""
    Сен IT рекрутерсің. 
    Сұрақ: {question}
    Кандидаттың жауабы: {user_answer}

    Тапсырма:
    1. Жауапты 10 балдық жүйемен бағала.
    2. Қандай қателер бар екенін айт.
    3. Дұрыс жауап қандай болуы керек екенін ҚАЗАҚ ТІЛІНДЕ түсіндір.
    """
    # Осы жерде AlemLLM-ге сұраныс жіберу коды (analyze_candidate_score сияқты)
    # ...

# indrive_api.py файлына қосу:
def transcribe_voice(file_path: str):
    """Дауыстық файлды Gemini арқылы мәтінге айналдыру"""
    # Мұнда Gemini-дің мультимодальдік мүмкіндігін қолданамыз
    # Әзірге біз AlemLLM қолданып жатқандықтан,
    # дауысты мәтінге айналдыру үшін Gemini 1.5 Flash моделін қосқан тиімді.
    return "Пайдаланушының дауыстық жауабы (транскрипция сәтті өтті)"


def analyze_candidate_score(user_text: str):
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "alemllm",
            "messages": [
                {
                    "role": "system",
                    "content": "Сен inDrive сарапшысысың. Кандидаттың мәтінін бағала (0-ден 1.0-ге дейін) және қысқаша кеңес бер. Жауапты саннан баста."
                },
                {"role": "user", "content": user_text}
            ]
        }
        response = requests.post(URL, json=payload, headers=headers, timeout=45)
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            match = re.search(r"(\d+[\.,]\d+)", content)
            if match:
                score = float(match.group(1).replace(",", "."))
                feedback = content.replace(match.group(0), "").strip(":,. ")
                return score, (feedback if feedback else "Жақсы жауап!")
            return 0.5, content
        return 0.0, f"Ошибка API: {response.status_code}"
    except Exception as e:
        return 0.0, f"Техникалық қате: {e}"

def send_to_backend(user_id, username, full_name, text, score, summary):
    """Деректерді автоматты түрде FastAPI-ге (Dashboard-қа) жіберу"""
    payload = {
        "user_id": user_id,
        "username": username or "unknown",
        "full_name": full_name,
        "answers_text": text,
        "ai_score": int(score * 100), # 0.85-ті 85-ке айналдырамыз
        "ai_summary": summary
    }
    try:
        requests.post(BACKEND_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Бэкендке жіберу кезіндегі қате: {e}")