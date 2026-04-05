from __future__ import annotations

from sqlalchemy import func, select

from database import SessionLocal
from models import Candidate


def seed_candidates() -> int:
    """
    Заполняет БД тестовыми кандидатами (если данных ещё нет).
    Возвращает количество добавленных кандидатов.
    """
    with SessionLocal() as db:

        existing_count = db.scalar(select(func.count()).select_from(Candidate))
        if existing_count and existing_count > 0:

            return 0

        candidates_data = [
            {
                "user_id": 1001,
                "username": "anna_k",
                "full_name": "Анна Кузнецова",
                "answers_text": "Умею работать с данными, люблю анализ и метрики. Привожу примеры проектов.",
                "ai_score": 92,
                "ai_summary": "Сильный кандидат: структура ответов, уверенный уровень мотивации.",
            },
            {
                "user_id": 1002,
                "username": "ivan_dev",
                "full_name": "Иван Петров",
                "answers_text": "Ответы краткие, но по делу. Есть опыт, однако мало конкретики по кейсам.",
                "ai_score": 67,
                "ai_summary": "Средний уровень: нужны уточнения по проектам и глубине решений.",
            },
            {
                "user_id": 1003,
                "username": None,
                "full_name": "Мария Смирнова",
                "answers_text": "Технические детали частично отсутствуют. Общие фразы, мало цифр и результатов.",
                "ai_score": 44,
                "ai_summary": "Требует проверки: слабая конкретика, необходимы уточняющие вопросы.",
            },
            {
                "user_id": 1004,
                "username": "serg_code",
                "full_name": "Сергей Иванов",
                "answers_text": "Хорошо объясняет подходы, показывает понимание процессов и рисков.",
                "ai_score": 83,
                "ai_summary": "Похоже на strong match: ясная логика и устойчивый стиль общения.",
            },
            {
                "user_id": 1005,
                "username": "olga_pm",
                "full_name": "Ольга Николаева",
                "answers_text": "Ответы адекватные, но формат местами разрозненный. Много вовлеченности.",
                "ai_score": 55,
                "ai_summary": "Промежуточно: возможен хороший потенциал после уточнения деталей.",
            },
        ]

        added = 0
        for item in candidates_data:
            db.add(Candidate(**item))
            added += 1

        db.commit()
        return added


if __name__ == "__main__":
    print(f"Добавлено кандидатов: {seed_candidates()}")

