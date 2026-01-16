from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field, Relationship

from db.models.hotel import Hotel


class RoomType(SQLModel, table=True):
    __tablename__ = 'room_types'
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"type_": BigInteger})
    hotel_id: int = Field(
        foreign_key="hotels.id",
        index=True,
        nullable=False,
        ondelete="CASCADE"
    )
    hotel: Optional["Hotel"] = Relationship(cascade_delete=True)
    name: str = Field(max_length=255, nullable=False)
    