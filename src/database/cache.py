import os
from datetime import timedelta
from typing import Union

from redis import StrictRedis
from redis.asyncio.client import Redis as AsyncRedis


class RedisClient:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    CONNECTION = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    ASYNC_CONNECTION = AsyncRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    @classmethod
    def get_async_connection(cls) -> AsyncRedis:
        return cls.ASYNC_CONNECTION

    @classmethod
    def hgetall(cls, key: str):
        return cls.CONNECTION.hgetall(key)

    @classmethod
    def hset(cls, key: str, data: dict) -> None:
        cls.CONNECTION.hset(key, mapping=data)

    @classmethod
    def expired(cls, key: str, ex: Union[int, timedelta]) -> None:
        cls.CONNECTION.expire(key, ex)

    @classmethod
    def incr(cls, key: str):
        return cls.CONNECTION.incr(key)
