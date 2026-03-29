import requests
import os
import re  # Добавили библиотеку для поиска чисел в тексте
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("INDRIVE_API_KEY")
URL = "https://llm.alem.ai/v1/chat/completions"


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
                    "content": "Ты эксперт inDrive. Оцени текст кандидата для inVision U. Выдай балл от 0 до 1.0 и краткий совет. Твой ответ должен начинаться с числа."
                },
                {"role": "user", "content": user_text}
            ]
        }

        response = requests.post(URL, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()

            # Улучшенный поиск числа (Score) в начале строки
            # Ищет что-то вроде "0.4" или "0,4" или "0.45"
            match = re.search(r"(\d+[\.,]\d+)", content)

            if match:
                score_str = match.group(1).replace(",", ".")  # Меняем запятую на точку для Python
                score = float(score_str)
                # Остальной текст после числа — это совет
                feedback = content.replace(match.group(0), "").strip(":,. ")
                return score, feedback if feedback else "Хороший ответ!"
            else:
                return 0.5, content  # Если число не найдено, возвращаем весь текст как фидбек
        else:
            return 0.0, f"Ошибка API: {response.status_code}"

    except Exception as e:
        print(f"Ошибка в коде: {e}")
        return 0.0, "Техническая заминка"