import base64
import json
import logging
import os
import time
import uuid
from logging.handlers import RotatingFileHandler
from typing import List, Tuple, Union

from fastapi import Request, Response
from starlette.middleware.base import _StreamingResponse

from src.const import TIME_UNIT


class Logger:

    ### The Block Only Execute When First Import
    service = "tinyurl"
    dir = f"/var/log/{service}"
    os.makedirs(dir, exist_ok=True)
    path = f"{dir}/log.txt"
    max_size = 10 * 1024 * 1024    # unit: bytes
    max_file = 5

    logger = logging.getLogger(service)

    try:
        handler = RotatingFileHandler(path, maxBytes=max_size, backupCount=max_file)
        formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception as err:
        print(f"Add handler fail: {err}")
        pass

    logger.setLevel(logging.INFO)

    LEVEL_INFO = "info"
    LEVEL_WARN = "warning"
    LEVEL_ERR = "error"
    ### ====================================== ###

    @classmethod
    def get_logger(cls):
        return cls.logger

    @classmethod
    def log_writer(cls, logging_event: Union[str, dict], level: str):
        msg = logging_event
        if isinstance(logging_event, dict):
            msg = json.dumps(logging_event)

        if level == cls.LEVEL_INFO:
            func = cls.logger.info
        elif level == cls.LEVEL_WARN:
            func = cls.logger.warning
        elif level == cls.LEVEL_ERR:
            func = cls.logger.error
        else:
            func = cls.logger.debug

        func(msg)

    @classmethod
    def batch_log_writer(cls, logging_events: List[dict]):
        for event_inner in logging_events:
            level = event_inner["level"]
            logging_event = event_inner["event"]
            cls.log_writer(logging_event, level)

    @classmethod
    async def get_request_log(cls, request: Request) -> dict:
        epoch_timestamp, date_timestamp = cls.get_current_date_and_timestamp()
        return {
            "request_url": request.url._url,
            "headers": dict(request.headers),
            "body": await cls.get_request_body(request),
            "path_parameter": request.path_params,
            "query_string_parameter": dict(request.query_params),
            "http_method": request.method,
            "epoch_timestamp": epoch_timestamp,
            "date_timestamp": date_timestamp,
            "log_type": "request",
            "source_ip": request.client.host,
            "request_id": cls.generate_request_id(),
        }

    @classmethod
    async def get_response_log(cls, request: Request, response: Response) -> dict:
        epoch_timestamp, date_timestamp = cls.get_current_date_and_timestamp()
        return {
            "request_url": request.url._url,
            "headers": dict(response.headers),
            "body": await cls.get_response_body(response),
            "path_parameter": request.path_params,
            "query_string_parameter": dict(request.query_params),
            "http_method": request.method,
            "epoch_timestamp": epoch_timestamp,
            "date_timestamp": date_timestamp,
            "status_code": response.status_code,
            "duration": epoch_timestamp - request.state.log["epoch_timestamp"],
            "log_type": "response",
            "source_ip": request.client.host,
            "request_id": request.state.log["request_id"],
        }

    @classmethod
    def generate_request_id(cls) -> str:
        return uuid.uuid4().hex

    @classmethod
    def get_current_date_and_timestamp(cls) -> Tuple[int, str]:
        current_ts = int(time.time() * TIME_UNIT)
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(current_ts // TIME_UNIT)) + f".{current_ts % TIME_UNIT}"
        return current_ts, date

    @classmethod
    async def get_request_body(cls, request: Request) -> str:
        request_body = await request.body()
        return cls.__bytes_to_str(request_body)

    @classmethod
    async def get_response_body(cls, response: Response) -> str:
        response_body = b"".join([chunk async for chunk in response.body_iterator])
        return cls.__bytes_to_str(response_body)

    @classmethod
    def get_log_level(cls, response: Response) -> str:
        if 200 <= response.status_code < 400:
            level = cls.LEVEL_INFO
        elif 400 <= response.status_code < 500:
            level = cls.LEVEL_WARN
        else:
            level = cls.LEVEL_ERR

        return level

    @classmethod
    def __bytes_to_str(cls, body: bytes) -> str:
        try:
            return body.decode("utf-8")
        except Exception as err:
            print(err)

        try:
            return base64.b64encode(body).decode("utf-8")
        except Exception as err:
            print(err)

        try:
            return body.hex()
        except Exception as err:
            print(err)

        return ""
