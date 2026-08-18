import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

def get_database_url() -> str:
    use_postgres = os.getenv("USE_POSTGRES", "false").lower() in ("true", "1")
    if use_postgres:
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"
    else:
        db_path = os.getenv("SQLITE_PATH", "ai_news_aggregator.db")
        return f"sqlite:///{db_path}"

db_url = get_database_url()
if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()


