import os

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.framework.utils import custom_callback, ip_identifier


def pytest_configure():
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """

    os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/tinyurl"
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_DB"] = "0"
    os.environ["RATE_LIMIT_TIMES"] = "10"
    os.environ["RATE_LIMIT_TIME_UNIT"] = "minutes"


@pytest.fixture()
def client(mocker):
    from main import app

    mocker.patch("main.FastAPILimiter.redis", fakeredis.aioredis.FakeRedis(db=0))
    mocker.patch("main.FastAPILimiter.identifier", ip_identifier)
    mocker.patch("main.FastAPILimiter.http_callback", custom_callback)
    mocker.patch("main.FastAPILimiter.lua_sha", "test")
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_db_init(mocker):
    mocker.patch("src.database.base.init_db")


@pytest.fixture(autouse=True)
def mock_db(mocker):
    mock_session = mocker.MagicMock(spec=Session)
    mocker.patch('src.database.base.SessionLocal', return_value=mock_session)
    return mock_session


@pytest.fixture(autouse=True)
async def mock_redis(mocker):
    mocker.patch('src.database.cache.RedisClient.CONNECTION', fakeredis.FakeStrictRedis(db=0, decode_responses=True))
    mocker.patch('src.database.cache.RedisClient.ASYNC_CONNECTION', fakeredis.aioredis.FakeRedis(db=0))
