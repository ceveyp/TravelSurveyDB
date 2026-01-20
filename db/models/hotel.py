from typing import Optional, List

from pydantic import ConfigDict
from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship

from db.models.hotel_chain import HotelChain


class Hotel(SQLModel, table=True):
    __tablename__ = 'hotels'
    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)
    chain_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("hotel_chains.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    chain: Optional["HotelChain"] = Relationship()
    contacts: Optional[List["HotelContact"]] = Relationship(back_populates="hotel")
    place_id: Optional[str] = Field(default=None, nullable=True, unique=True, index=True)
    cvent_id: Optional[int] = Field(default=None, nullable=True, unique=True, index=True)
    property_name: str = Field(max_length=500, nullable=False)
    address: str = Field(max_length=500, nullable=False)
    city: str = Field(max_length=255, nullable=False)
    state: str = Field(max_length=8, nullable=False)
    country: str = Field(max_length=45, nullable=False)
    postal_code: str = Field(max_length=45, nullable=False)
    phone: str = Field(max_length=45, nullable=False)
    url: str = Field(max_length=500, nullable=False, index=True)


class HotelContact(SQLModel, table=True):
    __tablename__ = 'contacts'

    model_config = ConfigDict(validate_assignment=True)

    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)
    hotel_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("hotels.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    hotel: Optional["Hotel"] = Relationship(back_populates="contacts")
    name: str = Field(..., max_length=255, nullable=False)
    title: str = Field(..., max_length=255, nullable=False)
    email: str = Field(..., max_length=255, nullable=False)
    phone: Optional[str] = Field(max_length=45, nullable=True, default=None)
    role: str = Field(..., max_length=45, nullable=False)
