from typing import Optional

from sqlmodel import SQLModel, Field


class MedicalCategory(SQLModel, table=True):
    __tablename__ = 'medical_categories'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, min_length=2, max_length=45)
