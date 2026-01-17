from sqlalchemy.orm import configure_mappers
from sqlmodel import SQLModel

import db.models
from utils.config import get_config

configure_mappers()

target_metadata = SQLModel.metadata

def get_db_url():
    config = get_config()
    return f"postgresql://{config.db_user}:{config.db_pass}@{config.db_host}:{config.db_port}/{config.db_name}"


if __name__ == '__main__':
    print(get_db_url())