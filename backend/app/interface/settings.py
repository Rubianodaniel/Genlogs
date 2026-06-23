"""Application settings (delivery-layer config).

A single ``Settings`` object holds environment-driven configuration. It is
exposed as a Singleton via ``functools.lru_cache`` so there is one source of
truth per process. Values are read from environment variables with safe local
defaults — no secrets hardcoded. We use ``os.getenv`` rather than a settings
library to keep dependencies minimal (KISS).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Tuple

# Local dev origins used when ``CORS_ORIGINS`` is not set.
_DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://localhost:3000"


def _parse_origins(raw: str) -> Tuple[str, ...]:
    """Split a comma-separated origins string into a clean tuple.

    Empty entries and surrounding whitespace are dropped. A tuple is returned
    so the cached ``Settings`` stays immutable / hashable.
    """

    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


@dataclass(frozen=True)
class Settings:
    """Immutable configuration for the API delivery layer."""

    cors_origins: Tuple[str, ...]

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins as a list (FastAPI/Starlette expects a list)."""

        return list(self.cors_origins)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Provide the shared ``Settings`` instance (Singleton).

    Reads ``CORS_ORIGINS`` (comma-separated) from the environment, defaulting to
    local dev origins. Cached so all callers share one instance.
    """

    raw_origins = os.getenv("CORS_ORIGINS", _DEFAULT_CORS_ORIGINS)
    return Settings(cors_origins=_parse_origins(raw_origins))
