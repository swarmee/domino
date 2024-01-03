
from pythonjsonlogger import jsonlogger
import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[logHandler])
logger = logging.getLogger(__name__)


class JSONLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        headers = dict(request.headers)
        correlation_id = headers.get("x-correlation-id", str(uuid.uuid4()))
        logger.info("Request", extra={
                    "path": request.url.path, "headers": headers, "correlation_id": correlation_id})
        response = await call_next(request)
        response.headers["x-correlation-id"] = correlation_id
        logger.info("Response", extra={
                    "status_code": response.status_code, "correlation_id": correlation_id})
        return response


