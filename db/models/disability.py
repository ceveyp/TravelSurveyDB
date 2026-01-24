from typing import Optional

from sqlalchemy import Column, BigInteger, ForeignKey
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
    definition: str = Field(nullable=False)
    impacted: int = Field(nullable=False)
    impacted_workforce: int = Field(nullable=False)
    likelihood: float = Field(nullable=False)
    labor_stat: float = Field(nullable=False)
    statistics: str = Field(nullable=False)
    statistics_source: str = Field(nullable=False, max_length=500)
    labor_source: str = Field(nullable=False, max_length=500)
    definition_source: str = Field(nullable=False, max_length=500)
