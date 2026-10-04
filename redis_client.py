import os

import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

redis_client = None

if REDIS_URL:
    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )


def get_cached_value(key: str):
    if redis_client is None:
        return None

    try:
        return redis_client.get(key)
    except redis.RedisError:
        return None


def set_cached_value(
    key: str,
    value: str,
    expiration: int = 30,
):
    if redis_client is None:
        return

    try:
        redis_client.setex(
            key,
            expiration,
            value,
        )
    except redis.RedisError:
        pass


def delete_cached_value(key: str):
    if redis_client is None:
        return

    try:
        redis_client.delete(key)
    except redis.RedisError:
        pass
