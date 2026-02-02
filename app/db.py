from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite file will be created in your project folder as tvmaze.db
DATABASE_URL = "sqlite:///./tvmaze.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for sqlite + FastAPI
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

def get_db():
    """
    FastAPI dependency that gives us a DB session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
