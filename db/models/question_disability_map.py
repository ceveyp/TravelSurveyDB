from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field, Relationship

from db.models.disability import Disability
from db.models.question import Question


class QuestionDisabilityMap(SQLModel, table=True):
    __tablename__ = 'question_disability_map'
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"type_": BigInteger})
    question_id: int = Field(
        foreign_key="questions.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    question: Optional["Question"] = Relationship()
    disability_id: int = Field(
        foreign_key="disabilities.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    disability: Optional["Disability"] = Relationship()
    reason: str = Field(nullable=False, max_length=1000)
