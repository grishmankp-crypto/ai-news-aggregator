import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

def get_database_url() -> str:
    # Priority 1: Standard DATABASE_URL (Neon, Supabase, Railway, Heroku, etc.)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        database_url = database_url.strip().strip("'\"")
        # Handle if the user pasted "DATABASE_URL=postgresql://..." into the secret
        if database_url.startswith("DATABASE_URL="):
            database_url = database_url.split("DATABASE_URL=", 1)[1].strip().strip("'\"")
        # Convert legacy postgres:// to postgresql:// for SQLAlchemy compatibility
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        if database_url:
            return database_url

    # Priority 2: Manual PostgreSQL config
    use_postgres = os.getenv("USE_POSTGRES", "false").lower() in ("true", "1")
    if use_postgres and os.getenv("POSTGRES_HOST"):
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    # Priority 3: Local SQLite (zero-config default)
    db_path = os.getenv("SQLITE_PATH", "ai_news_aggregator.db").strip().strip("'\"")
    return f"sqlite:///{db_path}"

db_url = get_database_url()
if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=60,  # Recycle connections every 60s (Neon free tier is aggressive)
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()
