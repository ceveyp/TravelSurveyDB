from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field, Relationship

from db.models.hotel_chain import HotelChain


class Hotel(SQLModel, table=True):
    __tablename__ = 'hotels'
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"type_": BigInteger})
    chain_id: int = Field(
        foreign_key="hotel_chains.id",
        index=True,
        nullable=False,
        ondelete="CASCADE"
    )
    chain: Optional["HotelChain"] = Relationship(cascade_delete=True)
    cvent_id: int = Field(default=None, nullable=False, unique=True, index=True)
    property_name: str = Field(max_length=500, nullable=False)
    address: str = Field(max_length=500, nullable=False)
    city: str = Field(max_length=255, nullable=False)
    state: str = Field(max_length=8, nullable=False)
    country: str = Field(max_length=45, nullable=False)
    postal_code: str = Field(max_length=45, nullable=False)
    phone: str = Field(max_length=45, nullable=False)
    url: str = Field(max_length=500, nullable=False, index=True)
