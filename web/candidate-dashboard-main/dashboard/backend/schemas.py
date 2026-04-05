import datetime as dt

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from pydantic import BaseModel



class BotDataIn(BaseModel):
    user_id: int
    username: str | None
    full_name: str
    answers_text: str
    ai_score: int
    ai_summary: str
    ai_probability: int

class CandidateOut(BaseModel):
    id: int
    user_id: int
    username: str | None
    full_name: str | None
    answers_text: str
    ai_score: int
    ai_summary: str | None
    ai_probability: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class CandidatesListOut(BaseModel):
    candidates: list[CandidateOut]

