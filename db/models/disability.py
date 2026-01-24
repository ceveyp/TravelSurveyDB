from typing import Optional

from sqlalchemy import Column, BigInteger, ForeignKey, Text
from sqlmodel import SQLModel, Field, Relationship


class Disability(SQLModel, table=True):
    __tablename__ = 'disabilities'
    id: Optional[int] = Field(default=None, primary_key=True)
    market_data: Optional["MarketData"] = Relationship(back_populates="disability")
    key: str = Field(nullable=False, index=True, unique=True)
    name: str = Field(nullable=False, min_length=2, max_length=45, unique=True)


class MarketData(SQLModel, table=True):
    __tablename__ = 'market_data'
    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)
    disability_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("disabilities.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    disability: Optional["Disability"] = Relationship(back_populates="market_data")
    definition: Optional[str] = Field(nullable=True, default=None, sa_type=Text)
    impacted: Optional[int] = Field(nullable=True, default=None)
    impacted_workforce: Optional[int] = Field(nullable=True, default=None)
    likelihood: Optional[float] = Field(nullable=True, default=None)
    labor_stat: Optional[float] = Field(nullable=True, default=None)
    statistics: Optional[str] = Field(nullable=True, default=None, sa_type=Text)
    statistics_source: Optional[str] = Field(nullable=True, default=None, sa_type=Text)
    labor_source: Optional[str] = Field(nullable=True, default=None, sa_type=Text)
    definition_source: Optional[str] = Field(nullable=True, default=None, sa_type=Text)
