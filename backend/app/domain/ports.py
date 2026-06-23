"""Ports (abstract interfaces) for the domain.

Use cases depend on these abstractions, not on concrete adapters
(Dependency Inversion). Infrastructure provides implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.domain.entities import Carrier, CityPair


class CarrierRepository(ABC):
    """Port for looking up carriers serving a city pair.

    The in-memory adapter implements this now; a real DB-backed adapter could
    replace it later without touching the use case.
    """

    @abstractmethod
    def find_by_city_pair(self, city_pair: CityPair) -> List[Carrier]:
        """Return the carriers for the given origin/destination pair.

        Implementations decide how to match (e.g. case-insensitive, alias
        tolerant) and what to return when no specific rule matches.
        """
        raise NotImplementedError
