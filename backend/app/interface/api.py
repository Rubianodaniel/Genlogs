"""FastAPI router for the carriers API (delivery layer).

Routes call the injected ``GetCarriersUseCase`` and map its result to DTOs.
The use case is provided via ``Depends`` (composition root in ``deps.py``),
which is the seam unit tests override.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.application.get_carriers import GetCarriersUseCase
from app.interface.deps import get_carriers_use_case
from app.interface.schemas import CarriersRequest, CarriersResponse, CityField

# Query-param variant of the shared city constraints (DRY): the same validation
# as the POST body, expressed through ``Query`` so the GET endpoint has no
# unvalidated path into the use case.
CityQuery = Annotated[
    CityField, Query(description="City name (validated)")
]

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""

    return {"status": "ok"}


@router.post("/carriers", response_model=CarriersResponse)
def carriers_post(
    payload: CarriersRequest,
    use_case: GetCarriersUseCase = Depends(get_carriers_use_case),
) -> CarriersResponse:
    """Return carriers for the origin/destination pair (JSON body)."""

    result = use_case.execute(payload.from_city, payload.to_city)
    return CarriersResponse.from_result(result)


@router.get("/carriers", response_model=CarriersResponse)
def carriers_get(
    from_city: CityQuery,
    to_city: CityQuery,
    use_case: GetCarriersUseCase = Depends(get_carriers_use_case),
) -> CarriersResponse:
    """Return carriers for the origin/destination pair (query params)."""

    result = use_case.execute(from_city, to_city)
    return CarriersResponse.from_result(result)
