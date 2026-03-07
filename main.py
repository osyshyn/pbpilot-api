import logging
import time
from collections.abc import Awaitable, Callable

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from starlette.responses import Response

from config.logger import configure_logging
from config.router import initialize_admin_panel, initialize_routers
from config.settings import Settings
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
logger = logging.getLogger(__name__)

settings = Settings.load()
configure_logging()

app = FastAPI(
    title=settings.API_TITLE,
    openapi_url='/openapi.json',
    root_path='/Prod',
)
handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

@app.middleware('http')
async def add_process_time_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers['X-Process-Time'] = f'{process_time:.4f}'
    logger.info(
        'Request: %s %s - Completed in: %.4fs',
        request.method,
        request.url.path,
        process_time,
    )
    return response


initialize_admin_panel(app)
main_api_router = initialize_routers()
app.include_router(main_api_router)


def main() -> None:
    """Run the application locally using uvicorn.

    Starts the FastAPI application on host 0.0.0.0 and port 8000.
    Used for local development and testing.

    """
    logger.info('Start')
    uvicorn.run('main:app', host='0.0.0.0', port=8000)  # noqa: S104


if __name__ == '__main__':
    main()
