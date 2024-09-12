from fastapi import APIRouter

from src.routers.v1.tinyurl import router as tinyurl_route

router = APIRouter(prefix="/v1")
router.include_router(tinyurl_route)
