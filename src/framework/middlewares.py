from fastapi import BackgroundTasks, FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.framework.logger import Logger


class LoggerMiddleware(BaseHTTPMiddleware):
    logger_skip_paths = ["/api/docs", "/api/redoc", "/"]

    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_log = await Logger.get_request_log(request)
        self.__state_request_log(request, request_log)
        Logger.log_writer(request_log, Logger.LEVEL_INFO)

        response: Response = await call_next(request)

        if request.url.path in self.logger_skip_paths:
            return response

        response_log = await Logger.get_response_log(request, response)

        background_tasks = BackgroundTasks()
        background_tasks.add_task(Logger.log_writer, response_log, Logger.get_log_level(response))

        new_response = Response(content=response_log["body"],
                                status_code=response.status_code,
                                headers=dict(response.headers),
                                media_type=response.media_type)
        new_response.background = background_tasks
        return new_response

    def __state_request_log(self, request: Request, request_log: dict):
        request.state.log = request_log
