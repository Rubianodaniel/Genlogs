"""Composition root: FastAPI dependency providers.

Wires concrete adapters into the use case (Factory) and shares a single
repository instance (Singleton via ``lru_cache``). This is the seam tests
override with ``app.dependency_overrides``.
"""

from __future__ import annotations

from functools import lru_cache

from app.application.get_carriers import GetCarriersUseCase
from app.domain.ports import CarrierRepository
from app.infrastructure.in_memory_carrier_repo import InMemoryCarrierRepo


@lru_cache(maxsize=1)
def get_carrier_repository() -> CarrierRepository:
    """Provide the shared in-memory repository (Singleton).

    One instance is reused across requests so the in-memory data is a single
    source of truth.
    """

    return InMemoryCarrierRepo()


def get_carriers_use_case() -> GetCarriersUseCase:
    """Build the use case with the repository injected (Factory + DI)."""

    return GetCarriersUseCase(repository=get_carrier_repository())
