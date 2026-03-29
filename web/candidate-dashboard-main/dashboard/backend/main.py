from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .database import SessionLocal, init_db
from .models import Candidate
from .schemas import BotDataIn, CandidateOut, CandidatesListOut
from .seed_data import seed_candidates


app = FastAPI(title="Candidate Assessment API")

# CORS: разрешаем запросы с фронтенда на другом порту.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # 1) Создаём таблицы в SQLite (если их нет).
    init_db()
    # 2) Чтобы сайт не был пустым, при первом запуске подкидываем тестовые данные.
    seed_candidates()


@app.post("/api/bot-data")
def post_bot_data(payload: BotDataIn) -> dict:
    """
    Принимает данные от Telegram-бота и сохраняет/обновляет кандидата.
    """
    with SessionLocal() as db:
        # Ищем кандидата по внешнему идентификатору Telegram-пользователя.
        candidate = db.scalar(
            select(Candidate).where(Candidate.user_id == payload.user_id)
        )

        if candidate is None:
            # Если кандидата ещё нет — создаём новую запись.
            candidate = Candidate(
                user_id=payload.user_id,
                username=payload.username,
                full_name=payload.full_name,
                answers_text=payload.answers_text,
                ai_score=payload.ai_score,
                ai_summary=payload.ai_summary,
            )
            db.add(candidate)
        else:
            # Если запись уже есть — обновляем актуальные поля.
            # Предполагаем, что бот шлёт "последнюю версию" ответов кандидата.
            candidate.username = payload.username
            candidate.full_name = payload.full_name
            candidate.answers_text = payload.answers_text
            candidate.ai_score = payload.ai_score
            candidate.ai_summary = payload.ai_summary

        # Сохраняем изменения в SQLite.
        db.commit()

        # Возвращаем простой ответ для отладки/логирования бота.
        return {"ok": True, "id": candidate.id}


@app.get("/api/candidates", response_model=CandidatesListOut)
def get_candidates() -> CandidatesListOut:
    """Возвращает список всех кандидатов, отсортированных по баллу."""
    with SessionLocal() as db:
        # Сортируем по баллу (ai_score) по убыванию, чтобы топ-кандидаты были сверху.
        stmt = select(Candidate).order_by(Candidate.ai_score.desc(), Candidate.id.asc())
        # Выполняем запрос и достаём все строки.
        candidates = db.scalars(stmt).all()
        # Превращаем ORM-модели в Pydantic-schemas для корректной сериализации в JSON.
        return CandidatesListOut(candidates=[CandidateOut.model_validate(c) for c in candidates])


@app.get("/api/candidates/{id}", response_model=CandidateOut)
def get_candidate_by_id(id: int) -> CandidateOut:
    """Возвращает детали кандидата по внутреннему `id`."""
    with SessionLocal() as db:
        # Ищем кандидата по внутреннему идентификатору таблицы.
        candidate = db.scalar(select(Candidate).where(Candidate.id == id))
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")
        # Возвращаем найденного кандидата как Pydantic-модель.
        return CandidateOut.model_validate(candidate)

