from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

# Түзету: Егер "cd backend" деп папка ішінде тұрсаң, нүктені алып тастаған дұрыс
# ОСЫЛАЙ ЖАЗ (басындағы нүктелерді өшір):
from database import SessionLocal, init_db
from models import Candidate
from schemas import BotDataIn, CandidateOut, CandidatesListOut
from seed_data import seed_candidates

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Барлық IP-ден сұраныс қабылдауға рұқсат беру
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Барлық жерден рұқсат
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/api/bot-data")
def post_bot_data(payload: BotDataIn) -> dict:
    with SessionLocal() as db:
        candidate = db.scalar(
            select(Candidate).where(Candidate.user_id == payload.user_id)
        )
        if candidate is None:
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
            candidate.username = payload.username
            candidate.full_name = payload.full_name
            candidate.answers_text = payload.answers_text
            candidate.ai_score = payload.ai_score
            candidate.ai_summary = payload.ai_summary
        db.commit()
        return {"ok": True, "id": candidate.id}

@app.get("/api/candidates", response_model=CandidatesListOut)
def get_candidates() -> CandidatesListOut:
    with SessionLocal() as db:
        stmt = select(Candidate).order_by(Candidate.ai_score.desc(), Candidate.id.asc())
        candidates = db.scalars(stmt).all()
        return CandidatesListOut(candidates=[CandidateOut.model_validate(c) for c in candidates])

@app.get("/api/candidates/{id}", response_model=CandidateOut)
def get_candidate_by_id(id: int) -> CandidateOut:
    with SessionLocal() as db:
        candidate = db.scalar(select(Candidate).where(Candidate.id == id))
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return CandidateOut.model_validate(candidate)