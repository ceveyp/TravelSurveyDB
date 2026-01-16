from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field, Relationship

from db.models.hotel import Hotel


class Contact(SQLModel, table=True):
    __tablename__ = 'contacts'
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"type_": BigInteger})
    hotel_id: int = Field(
        foreign_key="hotels.id",
        index=True,
        nullable=False,
        sa_column_kwargs={"ondelete": "CASCADE"}
    )
    hotel: Optional["Hotel"] = Relationship()
    name: str = Field(max_length=255, nullable=False)
    title: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, nullable=False)
    phone: str = Field(max_length=45, nullable=False)
