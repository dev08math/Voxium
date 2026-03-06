from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from voxium.api.routes import health_router, meetings_router
from voxium.config.context import create_context
from voxium.config.settings import VoxiumSettings

import logging

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(level=logging.WARNING, format=_LOG_FORMAT)

_settings_for_log = VoxiumSettings()

logging.getLogger("voxium").setLevel(
    logging.DEBUG if _settings_for_log.debug else logging.INFO
)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)

for _noisy in (
    "httpcore",
    "httpx",
    "urllib3",
    "openai._base_client",
    "python_multipart",
    "fsspec",
    "multipart",
):
    logging.getLogger(_noisy).setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: initialize context and ensure upload dir exists."""
    settings = VoxiumSettings()
    ctx = create_context(settings)
    app.state.ctx = ctx

    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)

    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Voxium", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(meetings_router)

    return app


app = create_app()
