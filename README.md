# 🚀 Career AI — Intelligent Talent Acquisition System

**InDrive_career_ai** — бұл заманауи HR-процестерді автоматтандыруға арналған интеллектуалды экожүйе. Жоба **AlemLLM** мүмкіндіктерін пайдалана отырып, кандидаттарды мультимодальды (мәтін, аудио, файл) талдау арқылы іріктеуді 80%-ға жылдамдатады.

---

## ✨ Негізгі мүмкіндіктер (Core Features)

- **Multi-mode AI Assistant:** - *Mentor Mode:* Кандидаттың білімін тексеру үшін техникалық сұрақтар қою.
  - *Consultant Mode:* Кандидатқа мансаптық кеңестер беру.
- **Voice Interaction:** Аудио-сұхбаттарды мәтінге айналдыру (STT) және мағыналық талдау.
- **Document Analysis:** `.docx` форматындағы түйіндемелер мен файлдарды автоматты сканерлеу.
- **Interactive Dashboard:** React-те жасалған админ-панель арқылы кандидаттардың рейтингін (AI Score) және статистикасын нақты уақыт режимінде бақылау.
- **Telegram Integration:** Рекрутерлер мен кандидаттар үшін ыңғайлы интерфейс.

---

## 🛠 Технологиялық стек (Tech Stack)

### Backend:
- **Python (Aiogram 3.x):** Боттың логикасы мен қолданушы интерфейсі.
- **FastAPI:** Dashboard-қа деректер беруге арналған API.
- **SQLite:** Пайдаланушы деректері мен режимдерін сақтау.
- **AlemLLM:** Терең нейрондық талдау және бағалау (NLP).

### Frontend:
- **React (TypeScript):** Динамикалық Dashboard интерфейсі.
- **Tailwind CSS:** Заманауи және адаптивті дизайн.
- **Recharts:** Кандидаттар статистикасын визуализациялау.

---

## 📂 Жоба құрылымы (Project Structure)

```text
├── main.py                # Боттың негізгі коды (Aiogram)
├── indrive_api.py         # Gemini AI және Voice интеграциясы
├── bot_data.db            # Локальді деректер базасы (SQLite)
├── web/                   # Web Dashboard (React & FastAPI)
│   ├── frontend/          # React қолданбасы
│   └── backend/           # FastAPI сервері
├── requirements.txt       # Қажетті библиотекалар
└── README.md              # Жоба сипаттамасы