from typing import Optional

from sqlmodel import SQLModel, Field


class Disability(SQLModel, table=True):
    __tablename__ = 'disabilities'
    id: Optional[int] = Field(default=None, primary_key=True)
    disability_key: str = Field(nullable=False, index=True, unique=True)
    name: str = Field(nullable=False, min_length=2, max_length=45, index=True, unique=True)
    description: str = Field(nullable=False, min_length=2, max_length=500)
