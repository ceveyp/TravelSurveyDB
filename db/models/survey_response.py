from datetime import datetime
from typing import Optional

from sqlalchemy import Column, BigInteger, ForeignKey, Text, DateTime, func
from sqlmodel import SQLModel, Field, Relationship

from db.models.hotel import Hotel


class SurveyResponse(SQLModel, table=True):
    __tablename__ = 'survey_responses'
    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)
    hotel_id: Optional[int] = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("hotels.id", ondelete="CASCADE"),
            nullable=True,
            index=True
        )
    )
    hotel: Optional["Hotel"] = Relationship()
    survey_id: int = Field(..., sa_type=BigInteger, nullable=False, index=True)
    response_id: int = Field(..., sa_type=BigInteger, nullable=False, index=True, unique=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    )
