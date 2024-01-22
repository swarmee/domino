import time
import uuid
import logging
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%SZ')
formatter.converter = time.gmtime  # Use UTC time
logHandler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[logHandler])
logger = logging.getLogger(__name__)

# Set the log level of pystan to CRITICAL
pystan_logger = logging.getLogger('pystan')
pystan_logger.setLevel(logging.CRITICAL)


class JSONLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Assign a correlation ID
        # Check if a correlation ID was provided in the request headers
        correlation_id = request.headers.get("correlation-id")

        # If no correlation ID was provided, generate a new one
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        request.state.correlation_id = correlation_id

        # Log the request
        logger.info("Request", extra={
            "path": request.url.path,
            "headers": dict(request.headers),
            "correlation_id": correlation_id
        })

        # Process the request
        response = await call_next(request)

        # Log the response
        processing_time = round((time.time() - start_time )* 1000, 5)
        logger.info("Response", extra={
            "status_code": response.status_code,
            "x-correlation_id": correlation_id,
            "x-processing_time_in_milliseconds": processing_time,
            "response_headers": dict(response.headers)
        })

        # Add the correlation ID to the response headers
        response.headers["x-correlation-id"] = correlation_id

        return response
