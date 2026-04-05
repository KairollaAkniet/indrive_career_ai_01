from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import SessionLocal, init_db
from models import Candidate
from schemas import BotDataIn, CandidateOut, CandidatesListOut

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/bot-data")
def post_bot_data(payload: BotDataIn):
    """
    Телеграм боттан келген деректерді қабылдау және сақтау.
    """
    with SessionLocal() as db:
        stmt = select(Candidate).where(Candidate.user_id == payload.user_id)
        candidate = db.scalar(stmt)

        if candidate is None:
            candidate = Candidate(
                user_id=payload.user_id,
                username=payload.username,
                full_name=payload.full_name,
                answers_text=payload.answers_text,
                ai_score=payload.ai_score,
                ai_summary=payload.ai_summary,
                ai_probability=payload.ai_probability
            )
            db.add(candidate)
        else:

            candidate.username = payload.username
            candidate.full_name = payload.full_name
            candidate.answers_text = payload.answers_text
            candidate.ai_score = payload.ai_score
            candidate.ai_summary = payload.ai_summary
            candidate.ai_probability = payload.ai_probability

        db.commit()
        db.refresh(candidate)
        return {"ok": True, "id": candidate.id}


@app.get("/api/candidates", response_model=CandidatesListOut)
def get_candidates():
    """
    Дашборд үшін барлық кандидаттар тізімін алу.
    """
    with SessionLocal() as db:
        stmt = select(Candidate).order_by(Candidate.ai_score.desc(), Candidate.id.asc())
        candidates = db.scalars(stmt).all()
        return CandidatesListOut(
            candidates=[CandidateOut.model_validate(c) for c in candidates]
        )


@app.get("/api/candidates/{id}", response_model=CandidateOut)
def get_candidate_by_id(id: int):
    """
    ID бойынша нақты бір кандидаттың мәліметін алу.
    """
    with SessionLocal() as db:
        candidate = db.scalar(select(Candidate).where(Candidate.id == id))
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return CandidateOut.model_validate(candidate)