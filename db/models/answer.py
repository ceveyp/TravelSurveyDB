from typing import Optional

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship

from db.models.hotel import Hotel
from db.models.question import Question
from db.models.room_type import RoomType


class Answer(SQLModel, table=True):
    __tablename__ = 'answers'
    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)
    room_type_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("room_types.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    room_type: Optional["RoomType"] = Relationship()
    hotel_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("hotels.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    hotel: Optional["Hotel"] = Relationship()
    question_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    question: Optional["Question"] = Relationship()
    raw_response: str = Field(min_length=1, nullable=False)
    normalized_score: float = Field(nullable=False)
