from math import ceil

from fastapi import HTTPException, Request, Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


def raise_http_error(status_code: int, reason: str, details: str) -> None:
    raise HTTPException(status_code=status_code, detail={"reason": reason, "details": details, "success": False})


async def ip_identifier(request: Request):
    service = request.headers.get("Service-Name")
    return service


async def custom_callback(request: Request, response: Response, pexpire: int):
    expire = ceil(pexpire / 1000)
    raise_http_error(status_code=HTTP_429_TOO_MANY_REQUESTS, reason="Too Many Requests", details=f"Too Many Requests. Retry after {expire} seconds")
