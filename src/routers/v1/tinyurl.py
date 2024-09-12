from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED

from src.const import RATE_LIMIT_SETUP
from src.database.actions import CrudHandler
from src.database.base import get_db
from src.framework.schemas import TinyUrlRequest, TinyUrlResponse

router = APIRouter(tags=["tinyurl"], dependencies=[Depends(RateLimiter(**RATE_LIMIT_SETUP))])


@router.api_route(path="/tinyurl", response_model=TinyUrlResponse, status_code=HTTP_201_CREATED, methods=["POST"])
async def create_tiny_url(url_data: TinyUrlRequest, request: Request, db: Session = Depends(get_db)) -> TinyUrlResponse:
    crud_handler = CrudHandler(db)
    url_obj = crud_handler.create_tiny_url(url_data.origin)
    tiny_url = request.url_for("redirect_tiny_url", tiny_url=url_obj.tiny)._url
    return TinyUrlResponse(tiny=tiny_url, origin=url_obj.origin, expired_date=url_obj.expired_date, success=True)


@router.api_route(path="/{tiny_url}", methods=["GET"])
def redirect_tiny_url(tiny_url: str, db: Session = Depends(get_db)) -> RedirectResponse:
    crud_handler = CrudHandler(db)
    url = crud_handler.get_origin_url(tiny_url)
    return RedirectResponse(url=url)
