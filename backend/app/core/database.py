from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Handle SQLite specific parameters
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models to ensure they are registered with Base.metadata
    from app.models import user, watchlist, snapshot, audit  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Keep local development databases usable after additive model changes.
    if settings.DATABASE_URL.startswith("sqlite"):
        inspector = inspect(engine)
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        with engine.begin() as connection:
            if "sensitivity_tier" not in user_columns:
                connection.execute(text(
                    "ALTER TABLE users ADD COLUMN sensitivity_tier VARCHAR(20) NOT NULL DEFAULT 'balanced'"
                ))
