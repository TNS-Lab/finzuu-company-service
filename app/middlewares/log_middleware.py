import time
import json
from fastapi import Request

from app.configs.logger import logger


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
        "headers": dict(request.headers),
        "body": json_body,
        'process_time': time.time() - start_time
    }
    logger.info(log_dict, extra=log_dict)

    return process
