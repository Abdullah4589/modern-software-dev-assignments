from __future__ import annotations

import logging
import sqlite3
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _describe_validation_error(error: dict[str, Any]) -> str:
    # Build a short "field: problem" message without echoing the client's input back.
    if error.get("type") == "json_invalid":
        return "request body is not valid JSON"
    location = [str(part) for part in error.get("loc", ())]
    field = ".".join(location[1:]) or "request body"
    return f"{field}: {error.get('msg', 'invalid value')}"


async def _validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    messages = [_describe_validation_error(error) for error in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "; ".join(messages)},
    )


async def _database_error_handler(request: Request, exc: sqlite3.Error) -> JSONResponse:
    # Full details go to the server log only; the client gets a generic message.
    logger.exception("Database error during %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "database error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(sqlite3.Error, _database_error_handler)
