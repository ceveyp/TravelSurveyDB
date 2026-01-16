from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field, Relationship

from db.models.question import Question
from db.models.travel_category import TravelCategory


class QuestionTravelCategoryMap(SQLModel, table=True):
    __tablename__ = 'question_travel_category_map'
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"type_": BigInteger})
    question_id: int = Field(
        foreign_key="questions.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    question: Optional["Question"] = Relationship()
    travel_category_id: int = Field(
        foreign_key="travel_categories.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    travel_category: Optional["TravelCategory"] = Relationship()
