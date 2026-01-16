from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field, Relationship

from db.models.hotel import Hotel
from db.models.question import Question
from db.models.room_type import RoomType


class Answer(SQLModel, table=True):
    __tablename__ = 'answers'
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"type_": BigInteger})
    room_type_id: int = Field(
        foreign_key="room_types.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    room_type: Optional["RoomType"] = Relationship()
    hotel_id: int = Field(
        foreign_key="hotels.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    hotel: Optional["Hotel"] = Relationship()
    question_id: int = Field(
        foreign_key="questions.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    question: Optional["Question"] = Relationship()
    raw_response: str = Field(min_length=1, nullable=False)
    normalized_score: float = Field(nullable=False)
