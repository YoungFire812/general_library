import time
from starlette.requests import Request
from loguru import logger


async def logging_middleware(request: Request, call_next):
    start_time = time.time()

    request_id = getattr(request.state, "request_id", None)

    user_id = getattr(request.state, "user_id", None)

    with logger.contextualize(
        request_id=request_id,
        user_id=user_id,
    ):
        response = await call_next(request)

        duration = round((time.time() - start_time) * 1000, 2)

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )

        return response