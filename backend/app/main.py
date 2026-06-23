"""Application factory for the Genlogs carriers API.

``create_app()`` is the Factory that assembles the FastAPI app: CORS plus the
mounted interface router. See ``specs/001-carriers-api.md``.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.interface.api import router


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

    app = FastAPI(title="Genlogs Carriers API", version="1.0.0")

    # CORS: allow all origins for the demo so the React client can call the API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app


# Module-level app instance for ``uvicorn app.main:app``.
app = create_app()
