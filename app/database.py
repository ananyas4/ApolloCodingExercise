"""Database setup and connection handling."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Local PostgreSQL connection (for development)
LOCAL_DB_URL = "postgresql://postgres:postgres@localhost:5432/vehicles"

# Use DATABASE_URL if set (for production), otherwise use local
db_url = os.getenv("DATABASE_URL", LOCAL_DB_URL)
is_production = os.getenv("DATABASE_URL") is not None

engine = create_engine(db_url)
db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency for db sessions."""
    session = db_session()
    try:
        yield session
    finally:
        session.close()


def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

