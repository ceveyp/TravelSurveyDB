from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field


class Question(SQLModel, table=True):
    __tablename__ = 'questions'
    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)
    question_text: str = Field(max_length=255, nullable=False)
    definition: str = Field(max_length=1000, nullable=False)
    notes: str = Field(max_length=1000, nullable=False)
    in_assessment: bool = Field(default=True, nullable=False)
    otc_code: int = Field(nullable=False, index=True)
    otc_list_name: str = Field(max_length=255, nullable=False)
    otc_category: str = Field(max_length=255, nullable=False)
    measurement_text: str = Field(max_length=255, nullable=False)
    survey_section: str = Field(max_length=255, nullable=False)
    applies_per_room_type: bool = Field(default=True, nullable=False)
