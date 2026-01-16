from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field, Relationship

from db.models.medical_category import MedicalCategory
from db.models.question import Question


class QuestionCategoryMap(SQLModel, table=True):
    __tablename__ = 'question_category_map'
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"type_": BigInteger})
    question_id: int = Field(
        foreign_key="questions.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    question: Optional["Question"] = Relationship()
    category_id: int = Field(
        foreign_key="medical_categories.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    category: Optional["MedicalCategory"] = Relationship()
