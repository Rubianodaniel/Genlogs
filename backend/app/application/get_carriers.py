"""Use case: get the carriers serving an origin/destination pair.

Depends only on the ``CarrierRepository`` port (Dependency Inversion). No
FastAPI/HTTP knowledge lives here. The concrete repository is injected by the
composition root in the interface layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.domain.entities import Carrier, CityPair
from app.domain.ports import CarrierRepository


@dataclass(frozen=True)
class GetCarriersResult:
    """Result of the use case: the echoed pair plus the matched carriers."""

    from_city: str
    to_city: str
    carriers: List[Carrier]


class GetCarriersUseCase:
    """Returns the carriers moving the highest volume between two cities."""

    def __init__(self, repository: CarrierRepository) -> None:
        self._repository = repository

    def execute(self, from_city: str, to_city: str) -> GetCarriersResult:
        """Look up carriers for the pair and echo the original city strings."""

        city_pair = CityPair(from_city=from_city, to_city=to_city)
        carriers = self._repository.find_by_city_pair(city_pair)
        return GetCarriersResult(
            from_city=from_city,
            to_city=to_city,
            carriers=carriers,
        )
