import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class BotDataIn(BaseModel):
    user_id: int
    username: str | None = None
    full_name: str | None = None
    answers_text: str
    ai_score: int = Field(ge=0, le=100)
    ai_summary: str | None = None


class CandidateOut(BaseModel):
    id: int
    user_id: int
    username: str | None
    full_name: str | None
    answers_text: str
    ai_score: int
    ai_summary: str | None
    created_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class CandidatesListOut(BaseModel):
    candidates: list[CandidateOut]

