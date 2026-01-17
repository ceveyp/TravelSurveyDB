from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.config import get_config


def get_db_url():
    config = get_config()
    return f"postgresql://{config.db_user}:{config.db_pass}@{config.db_host}:{config.db_port}/{config.db_name}"


engine = create_engine(
    get_db_url(),
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)

Session = sessionmaker(bind=engine)
