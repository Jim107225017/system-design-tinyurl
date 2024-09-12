import time
from datetime import datetime

from src.const import TIME_UNIT


def get_current_ts() -> int:
    return int(time.time() * TIME_UNIT)


def convert_datetime_to_ts(dt: datetime) -> int:
    return int(dt.timestamp() * TIME_UNIT)
