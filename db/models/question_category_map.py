from typing import Optional

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship

from db.models.medical_category import MedicalCategory
from db.models.question import Question


class QuestionCategoryMap(SQLModel, table=True):
    __tablename__ = 'question_category_map'
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
    category_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("medical_categories.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    category: Optional["MedicalCategory"] = Relationship()
