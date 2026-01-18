from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field


class Question(SQLModel, table=True):
    __tablename__ = "questions"

    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)

    question_text: str = Field(max_length=255, nullable=False)
    question_key: str = Field(max_length=255, nullable=False, index=True)

    definition: str = Field(max_length=1000)
    notes: Optional[str] = Field(max_length=1000)

    question_type: str = Field(nullable=False, index=True, max_length=16)
    question_type_notes: Optional[str] = Field(max_length=255)

    in_assessment: bool = Field(default=True, nullable=False)

    otc_code: Optional[int] = Field(index=True)
    otc_list_name: Optional[str] = Field(max_length=255)
    otc_category: Optional[str] = Field(max_length=255)

    measurement_text: Optional[str] = Field(max_length=255)
    survey_section: str = Field(max_length=255, nullable=False)

    applies_per_room_type: bool = Field(default=True, nullable=False)
