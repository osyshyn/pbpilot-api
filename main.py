import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.logger import configure_logging
from config.router import initialize_routers
from config.settings import Settings

logger = logging.getLogger(__name__)

settings = Settings.load()
configure_logging()

app = FastAPI(
    title=settings.API_TITLE,
    openapi_url='/openapi.json',
    root_path='/Prod',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
