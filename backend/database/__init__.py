from sqlmodel import Session, create_engine, SQLModel
import os
from dotenv import load_dotenv
load_dotenv()


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session