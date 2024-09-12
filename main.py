from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi_limiter import FastAPILimiter

from src.database.base import init_db
from src.database.cache import RedisClient
from src.framework.middlewares import LoggerMiddleware
from src.framework.utils import custom_callback, ip_identifier
from src.routers import router

init_db()


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = RedisClient.get_async_connection()
    await FastAPILimiter.init(
        redis=redis_connection,
        identifier=ip_identifier,
        http_callback=custom_callback,
    )
    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(LoggerMiddleware)
app.include_router(router)


@app.get("/")
def healthy_check():
    return Response(content="Hello World!", status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:app", host="0.0.0.0", port=5050, workers=2, proxy_headers=True, forwarded_allow_ips="*")
