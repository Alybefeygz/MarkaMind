from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .settings import settings

# Initialize database components as None
engine = None
SessionLocal = None
Base = declarative_base()

try:
    # Supabase PostgreSQL connection (only if psycopg2 is available)
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=30,
        echo=settings.DEBUG
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except ImportError:
    # psycopg2 not installed - database will be initialized later
    pass


def get_db():
    """Dependency to get database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Install psycopg2-binary and configure DATABASE_URL.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()