from sqlalchemy.orm import declarative_base, configure_mappers
from sqlmodel import SQLModel

Base = declarative_base()

import db.models

configure_mappers()

target_metadata = SQLModel.metadata
