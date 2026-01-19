from typing import Optional

from sqlmodel import SQLModel, Field


class TravelCategory(SQLModel, table=True):
    __tablename__ = 'travel_categories'
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(nullable=False, index=True, unique=True)
    name: str = Field(nullable=False, min_length=2, max_length=45, unique=True)
