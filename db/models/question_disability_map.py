from typing import Optional

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship

from db.models.disability import Disability
from db.models.question import Question


class QuestionDisabilityMap(SQLModel, table=True):
    __tablename__ = 'question_disability_map'
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
    disability_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("disabilities.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    disability: Optional["Disability"] = Relationship()
    reason: str = Field(nullable=False, max_length=1000)
