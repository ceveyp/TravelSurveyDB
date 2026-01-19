from typing import Optional, Literal

from pydantic import BaseModel
from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field

from constants.spreadsheet.field_types import QuestionDataTypes


StringBooleanRep = Literal['yes', 'no']


class QuestionInputValidator(BaseModel):
    question_type: QuestionDataTypes
    is_range: StringBooleanRep
    applies_per_room_type: StringBooleanRep
    in_assessment: StringBooleanRep


class Question(SQLModel, table=True):
    __tablename__ = "questions"

    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)

    question_text: str = Field(max_length=255, nullable=False)
    question_key: str = Field(max_length=255, nullable=False, index=True)

    definition: str = Field(max_length=1000)
    notes: Optional[str] = Field(max_length=1000)

    question_type: str = Field(nullable=False, index=True, max_length=16)
    question_type_notes: Optional[str] = Field(max_length=255)
    is_range: bool = Field(nullable=False, default=False)

    in_assessment: bool = Field(default=True, nullable=False)

    otc_code: Optional[int] = Field(index=True)
    otc_list_name: Optional[str] = Field(max_length=255)
    otc_category: Optional[str] = Field(max_length=255)

    measurement_text: Optional[str] = Field(max_length=255)
    survey_section: str = Field(max_length=255, nullable=False)

    applies_per_room_type: bool = Field(default=True, nullable=False)
