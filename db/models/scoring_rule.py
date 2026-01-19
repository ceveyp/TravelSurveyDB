from typing import Optional

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship

from db.models.question import Question


class ScoringRule(SQLModel, table=True):
    __tablename__ = 'scoring_rules'
    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)
    question_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    question: Optional["Question"] = Relationship()
    operator: str = Field(nullable=False, max_length=4, index=True, default='==')
    threshold_min: Optional[float] = Field(default=None, nullable=True)
    threshold_max: Optional[float] = Field(default=None, nullable=True)
    max_score: float = Field(nullable=False)
