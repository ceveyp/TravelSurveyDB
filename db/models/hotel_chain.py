from typing import Optional

from sqlmodel import SQLModel, Field


class HotelChain(SQLModel, table=True):
    __tablename__ = 'hotel_chains'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=255, nullable=False, index=True, unique=True)
    brand: str = Field(min_length=2, max_length=255, nullable=False, index=True)
