from builtins import Exception


class URLExpiredException(Exception):

    def __init__(self, message: str = "URL has expired"):
        super().__init__(message)


class URLNotFoundException(Exception):

    def __init__(self, message: str = "URL not found"):
        super().__init__(message)
