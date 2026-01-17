from typing import Optional

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship

from db.models.disability import Disability


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
    disability: Optional["Disability"] = Relationship()
    definition: str = Field(nullable=False)
    impacted: int = Field(nullable=False)
    impacted_workforce: int = Field(nullable=False)
    likelihood: float = Field(nullable=False)
    labor_stat: float = Field(nullable=False)
    statistics: str = Field(nullable=False)
    statistics_source: str = Field(nullable=False, max_length=500)
    labor_source: str = Field(nullable=False, max_length=500)
    definition_source: str = Field(nullable=False, max_length=500)
