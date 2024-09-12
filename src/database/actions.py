from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND, HTTP_410_GONE, HTTP_500_INTERNAL_SERVER_ERROR

from src.const import BASE62_ALPHABET, MAX_TINY_URL_LENGTH, URL_EXPIRED_DATE, URL_RELATION_KEY
from src.database.cache import RedisClient
from src.database.models import UrlCache, UrlRelation
from src.exceptions import URLExpiredException, URLNotFoundException
from src.framework.utils import raise_http_error
from src.timing import convert_datetime_to_ts, get_current_ts


class CrudHandler():

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_tiny_url(self, origin_url: str) -> UrlRelation:
        try:
            url_relation = self.__create_tiny_url_in_sql(origin_url)
            self.__create_tiny_url_in_cache(url_relation)
        except Exception as err:
            self.db.rollback()
            raise_http_error(status_code=HTTP_500_INTERNAL_SERVER_ERROR, reason="Create Tiny URL Fail", details=f"Create Tiny URL Fail: {err}")

        return url_relation

    def get_origin_url(self, tiny_url: str) -> str:
        try:
            index = self.__decode_base62(tiny_url)
            if cache_data := self.__get_origin_url_in_cache(index):
                if cache_data.expired_date < get_current_ts():
                    raise URLExpiredException()
                else:
                    return cache_data.origin

            url_relation = self.__get_origin_url_in_sql(index)
            if not url_relation:
                raise URLNotFoundException()

            if convert_datetime_to_ts(url_relation.expired_date) < get_current_ts():
                raise URLExpiredException()

            self.__create_tiny_url_in_cache(url_relation)

        except URLNotFoundException as err:
            raise_http_error(status_code=HTTP_404_NOT_FOUND, reason="Get Origin URL Fail", details=f"Get Origin URL Fail: {err}")

        except URLExpiredException as err:
            raise_http_error(status_code=HTTP_410_GONE, reason="Get Origin URL Fail", details=f"Get Origin URL Fail: {err}")

        except Exception as err:
            raise_http_error(status_code=HTTP_500_INTERNAL_SERVER_ERROR, reason="Get Origin URL Fail", details=f"Get Origin URL Fail: {err}")

        return url_relation.origin

    def __create_tiny_url_in_sql(self, origin_url: str) -> UrlRelation:
        index = RedisClient.incr(URL_RELATION_KEY)
        base62_str = self.__encode_base62(index)
        url_relation = UrlRelation(id=index,
                                   origin=origin_url,
                                   tiny=base62_str,
                                   expired_date=datetime.now(timezone.utc) + timedelta(days=URL_EXPIRED_DATE))
        self.db.add(url_relation)
        self.db.commit()
        return url_relation

    def __create_tiny_url_in_cache(self, url_relation: UrlRelation) -> None:
        cache_key = self.__get_tiny_url_cache_key(url_relation.id)
        cache_data = UrlCache(origin=url_relation.origin, expired_date=convert_datetime_to_ts(url_relation.expired_date)).model_dump()
        RedisClient.hset(cache_key, cache_data)
        self.__set_tiny_url_ttl(cache_key)

    def __get_origin_url_in_sql(self, index: int) -> UrlRelation:
        return self.db.query(UrlRelation).filter(UrlRelation.id == index).first()

    def __get_origin_url_in_cache(self, index: int) -> Optional[UrlCache]:
        cache_key = self.__get_tiny_url_cache_key(index)
        cache_data = RedisClient.hgetall(cache_key)
        if not cache_data:
            return

        return UrlCache(**cache_data)

    def __encode_base62(self, num: int) -> str:
        if num == 0:
            return BASE62_ALPHABET[0].rjust(MAX_TINY_URL_LENGTH, BASE62_ALPHABET[0])

        base62 = []
        while num:
            num, rem = divmod(num, 62)
            base62.append(BASE62_ALPHABET[rem])

        encoded = "".join(reversed(base62))
        return encoded.rjust(MAX_TINY_URL_LENGTH, BASE62_ALPHABET[0])

    def __decode_base62(self, base62_str: str) -> int:
        num = 0
        for char in base62_str:
            num = num * 62 + BASE62_ALPHABET.index(char)
        return num

    def __get_tiny_url_cache_key(self, index: int) -> str:
        return f"tiny_url_id_{index}"

    def __set_tiny_url_ttl(self, key: str) -> None:
        RedisClient.expired(key, ex=timedelta(days=1))
