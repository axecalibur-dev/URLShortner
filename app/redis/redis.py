import os

from dotenv import load_dotenv
from redis.asyncio import Redis

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "host.docker.internal")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    if REDIS_PASSWORD:
        REDIS_URL = (
            f"redis://:{REDIS_PASSWORD}"
            f"@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        )
    else:
        REDIS_URL = (
            f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        )


# Application-level Redis client.
# The client manages its own connection pool.
redis_client = Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


async def check_redis_connection() -> dict:
    result = await redis_client.ping()

    return {
        "status": "connected" if result else "failed",
    }


async def close_redis_connection():
    await redis_client.aclose()