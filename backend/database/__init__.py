import logging
from sqlmodel import Session, create_engine, SQLModel
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

logger.info(f"Connecting to database: {DATABASE_URL.replace('@', '[@]').replace(':', '[:]') if DATABASE_URL else 'None'}")

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

def create_db_and_tables():
    """Create database tables"""
    logger.info("Creating database tables...")
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def get_session():
    logger.debug("Opening database session")
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error in database session: {str(e)}")
            raise
        finally:
            logger.debug("Closing database session")