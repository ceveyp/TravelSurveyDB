from typing import Optional, Literal

from pydantic import BaseModel
from sqlalchemy import BigInteger, Text, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship

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
    scoring_rule: Optional["ScoringRule"] = Relationship(back_populates="question")

    question_text: str = Field(nullable=False, sa_type=Text)
    question_key: str = Field(nullable=False, index=True, sa_type=Text)

    definition: str = Field(sa_type=Text)
    notes: Optional[str] = Field(sa_type=Text)

    question_type: str = Field(nullable=False, index=True, max_length=16)
    question_type_notes: Optional[str] = Field(sa_type=Text)
    is_range: bool = Field(nullable=False, default=False)

    in_assessment: bool = Field(default=True, nullable=False)

    otc_code: Optional[int] = Field(index=True)
    otc_list_name: Optional[str] = Field(max_length=255)
    otc_category: Optional[str] = Field(max_length=255)

    measurement_text: Optional[str] = Field(max_length=255)
    survey_section: Optional[str] = Field(max_length=255, nullable=True, default=None)

    applies_per_room_type: bool = Field(default=True, nullable=False)


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
    question: Optional["Question"] = Relationship(back_populates="scoring_rule")
    operator: str = Field(nullable=False, max_length=4, index=True, default='==')
    threshold_min: Optional[float] = Field(default=None, nullable=True)
    threshold_max: Optional[float] = Field(default=None, nullable=True)
    max_score: float = Field(nullable=False)
