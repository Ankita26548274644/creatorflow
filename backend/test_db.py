from sqlalchemy import create_engine, text
from app.config import settings

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print("Database connection successful!")
        print(f"PostgreSQL version: {version}")
except Exception as e:
    print(f"Database connection failed: {e}")