from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import IntegrityError
from src.core.sqlErrors import is_error, UNIQUE_VIOLATION, NOT_NULL_VIOLATION, FOREIGN_KEY_VIOLATION
from sqlalchemy.exc import SQLAlchemyError


async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", None)

    if exc.status_code >= 500:
        logger.error(
            "http_error",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            method=request.method,
        )
    else:
        logger.warning(
            "http_error",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            method=request.method,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request_id,
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)

    if isinstance(exc, IntegrityError):
        if await is_error(exc, UNIQUE_VIOLATION):
            detail = "object with this data already exists"
            status = 409

        elif await is_error(exc, NOT_NULL_VIOLATION):
            detail = "some data cannot be None"
            status = 400

        elif await is_error(exc, FOREIGN_KEY_VIOLATION):
            detail = "invalid reference"
            status = 400

        else:
            detail = "Database integrity error"
            status = 500

        log_data = dict(
            detail=detail,
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
        )

        if status >= 500:
            logger.error("db_integrity_error", **log_data)
        else:
            logger.warning("db_integrity_error", **log_data)

        return JSONResponse(
            status_code=status,
            content={
                "detail": detail,
                "request_id": request_id,
            }
        )

    elif isinstance(exc, SQLAlchemyError):
        logger.exception(
            "db_error",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database error",
                "request_id": request_id,
            }
        )

    else:
        logger.exception(
            "unhandled_error",
            error=str(exc),
            path=request.url.path,
            method=request.method,
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
            }
        )