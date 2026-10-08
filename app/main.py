import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.database import check_db_connection
from app.redis.redis import check_redis_connection, close_redis_connection

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # -------------------------
    # Application startup
    # -------------------------

    # Check PostgreSQL connection
    try:
        db_info = await check_db_connection()

        logger.info(
            "PostgreSQL connected successfully | "
            "user=%s | database=%s",
            db_info["user"],
            db_info["database"],
        )

    except Exception:
        logger.exception("Failed to connect to PostgreSQL")
        raise

    # Check Redis connection
    try:
        redis_info = await check_redis_connection()

        logger.info(
            "Redis connected successfully | status=%s",
            redis_info["status"],
        )

    except Exception:
        logger.exception("Failed to connect to Redis")
        raise

    # Application is ready
    yield

    # -------------------------
    # Application shutdown
    # -------------------------

    await close_redis_connection()

    logger.info("Redis connection closed")
    logger.info("Application shutting down")


app = FastAPI(
    title="URL Shortener API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    db_status = "connected"
    db_details = {}
    try:
        db_details = await check_db_connection()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    redis_status = "connected"
    try:
        redis_info = await check_redis_connection()
        redis_status = redis_info.get("status", "unknown")
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"

    is_healthy = db_status == "connected" and redis_status == "connected"
    return {
        "status": "ok" if is_healthy else "degraded",
        "database": db_status,
        "database_info": {
            "user": db_details.get("user"),
            "database": db_details.get("database"),
        } if db_status == "connected" else None,
        "redis": redis_status,
    }