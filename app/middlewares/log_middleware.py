import time
import json
from fastapi import Request

from app.configs.logger import logger


SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key"}
SENSITIVE_FIELDS = {
    "access_token",
    "refresh_token",
    "token",
    "password",
    "secret",
    "authorization",
    "cookie",
}


def sanitize_headers(headers: dict) -> dict:
    return {
        key: "***" if key.lower() in SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }


def sanitize_body(value):
    if isinstance(value, dict):
        return {
            key: "***" if key.lower() in SENSITIVE_FIELDS else sanitize_body(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [sanitize_body(item) for item in value]

    return value


async def log_middleware(request: Request, call_next):
    start_time = time.time()

    body_bytes = await request.body()
    try:
        body = body_bytes.decode("utf-8")
        json_body = json.loads(body) if body else {}
    except Exception:
        json_body = body_bytes.decode("utf-8", errors="ignore")

    async def receive():
        return {"type": "http.request", "body": body_bytes, "more_body": False}

    process = await call_next(Request(request.scope, receive))

    log_dict = {
        "url": request.url.path,
        "method": request.method,
        "headers": sanitize_headers(dict(request.headers)),
        "body": sanitize_body(json_body),
        'process_time': time.time() - start_time
    }
    logger.info(log_dict, extra=log_dict)

    return process
