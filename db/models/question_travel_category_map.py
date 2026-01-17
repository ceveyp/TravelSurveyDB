from typing import Optional

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship

from db.models.question import Question
from db.models.travel_category import TravelCategory


class QuestionTravelCategoryMap(SQLModel, table=True):
    __tablename__ = 'question_travel_category_map'
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
    travel_category_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("travel_categories.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    travel_category: Optional["TravelCategory"] = Relationship()
