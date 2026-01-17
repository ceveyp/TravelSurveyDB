from typing import Optional

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship

from db.models.hotel import Hotel


class RoomType(SQLModel, table=True):
    __tablename__ = 'room_types'
    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)
    hotel_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("hotels.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    hotel: Optional["Hotel"] = Relationship()
    name: str = Field(max_length=255, nullable=False)
