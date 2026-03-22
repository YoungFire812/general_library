from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


def key_func(request: Request):
    return get_remote_address(request)


limiter = Limiter(key_func=key_func)