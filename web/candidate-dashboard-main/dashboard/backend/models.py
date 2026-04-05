import datetime as dt
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, Float
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)

    answers_text: Mapped[str] = mapped_column(Text, nullable=False)
    ai_score: Mapped[int] = mapped_column(Integer, nullable=False)
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True)


    ai_probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=dt.datetime.utcnow
    )

    __table_args__ = (UniqueConstraint("user_id", name="uq_candidates_user_id"),)