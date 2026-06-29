from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

# Attempt to configure engine with PostgreSQL first, then fallback to SQLite if needed
try:
    if settings.DATABASE_URL.startswith("postgresql"):
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            logger.info("Connected to PostgreSQL successfully.")
    else:
        raise ValueError("Not a Postgres URL")
except Exception as e:
    if settings.SQLITE_FALLBACK:
        logger.warning(f"Failed to connect to PostgreSQL ({e}). Falling back to SQLite at {settings.SQLITE_URL}")
        engine = create_engine(settings.SQLITE_URL, connect_args={"check_same_thread": False})
    else:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
