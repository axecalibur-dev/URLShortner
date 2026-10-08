import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

# Build database URL from environment variables with fallback
DB_USER = os.getenv("DB_USER", "shorturl_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "shorturldb")

DEFAULT_DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Convert standard PostgreSQL URLs to asyncpg URLs if necessary
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )
elif DATABASE_URL.startswith("postgresql+psycopg2://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql+psycopg2://",
        "postgresql+asyncpg://",
        1,
    )


# Async SQLAlchemy engine
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
)


# Async session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Declarative base
class Base(DeclarativeBase):
    pass


# FastAPI dependency
async def get_db():
    async with SessionLocal() as db:
        yield db


# Database health check
async def check_db_connection() -> dict:
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT current_user, current_database(), version();"
            )
        )

        row = result.fetchone()

        return {
            "status": "connected",
            "user": row[0],
            "database": row[1],
            "version": row[2],
        }