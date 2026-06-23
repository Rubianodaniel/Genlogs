"""Application factory for the Genlogs carriers API.

``create_app()`` is the Factory that assembles the FastAPI app: hardened CORS
(origins from configuration), security headers, a generic error handler that
never leaks internals, and the mounted interface router. See
``specs/001-carriers-api.md`` and ``specs/003-backend-validation-security.md``.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.interface.api import router
from app.interface.settings import get_settings

# Security headers applied to every response.
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

    settings = get_settings()
    app = FastAPI(title="Genlogs Carriers API", version="1.0.0")

    # CORS: restrict to configured origins (never "*"). Methods limited to what
    # the API actually serves. No credentials — this is a public, cookieless API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """Attach baseline security headers to every response."""

        response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Return a generic 500 with no traceback / internal details."""

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )

    app.include_router(router)
    return app


# Module-level app instance for ``uvicorn app.main:app``.
app = create_app()
