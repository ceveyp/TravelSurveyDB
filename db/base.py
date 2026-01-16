from sqlalchemy.orm import configure_mappers
from sqlmodel import SQLModel

import db.models

configure_mappers()

target_metadata = SQLModel.metadata
