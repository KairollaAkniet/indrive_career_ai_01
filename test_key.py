import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("ALEM_API_KEY")

print(f"Проверяю ключ: {key[:10]}...")
url = "https://api.plus.alem.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
data = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Привет! Ты работаешь?"}]
}

response = requests.post(url, json=data, headers=headers)

print(f"Статус: {response.status_code}")
print(f"Ответ: {response.text}")