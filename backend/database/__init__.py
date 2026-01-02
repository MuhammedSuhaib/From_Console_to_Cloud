from sqlmodel import Session, create_engine, SQLModel
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/todo_db")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

from contextlib import contextmanager

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session