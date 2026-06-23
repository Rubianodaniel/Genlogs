"""In-memory implementation of the ``CarrierRepository`` port.

This adapter is the single source of truth for the spec mapping
(city-pair -> carriers), reproduced verbatim from ``specs/001-carriers-api.md``.
It also owns city matching: case-insensitive, trimmed, whitespace-collapsed,
and tolerant of common variants via an alias table.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from app.domain.entities import Carrier, CityPair
from app.domain.ports import CarrierRepository

# Canonical city keys used internally for matching.
_NYC = "nyc"
_SF = "sf"
_WASHINGTON_DC = "washington_dc"
_LA = "la"

# Alias table: normalized (lowercased/trimmed) input -> canonical city key.
# City matching is case-insensitive and tolerant of common variants.
_CITY_ALIASES: Dict[str, str] = {
    # New York City
    "nyc": _NYC,
    "new york": _NYC,
    "new york city": _NYC,
    # San Francisco
    "sf": _SF,
    "san francisco": _SF,
    # Washington DC
    "washington dc": _WASHINGTON_DC,
    "washington": _WASHINGTON_DC,
    "dc": _WASHINGTON_DC,
    "washington d.c.": _WASHINGTON_DC,
    # Los Angeles
    "la": _LA,
    "los angeles": _LA,
}

# Carrier rules keyed by (origin canonical key, destination canonical key).
# Data is reproduced verbatim from the spec.
_RULES: Dict[Tuple[str, str], List[Carrier]] = {
    (_NYC, _WASHINGTON_DC): [
        Carrier(name="Knight-Swift Transport Services", trucks_per_day=10),
        Carrier(name="J.B. Hunt Transport Services Inc", trucks_per_day=7),
        Carrier(name="YRC Worldwide", trucks_per_day=5),
    ],
    (_SF, _LA): [
        Carrier(name="XPO Logistics", trucks_per_day=9),
        Carrier(name="Schneider", trucks_per_day=6),
        Carrier(name="Landstar Systems", trucks_per_day=2),
    ],
}

# Fallback for any other city pair.
_DEFAULT_CARRIERS: List[Carrier] = [
    Carrier(name="UPS Inc.", trucks_per_day=11),
    Carrier(name="FedEx Corp", trucks_per_day=9),
]


class InMemoryCarrierRepo(CarrierRepository):
    """Repository backed by the hardcoded spec data (no database)."""

    @staticmethod
    def _normalize_city(city: str) -> Optional[str]:
        """Normalize a raw city string to its canonical key, or ``None``."""

        key = " ".join(city.strip().lower().split())
        return _CITY_ALIASES.get(key)

    def find_by_city_pair(self, city_pair: CityPair) -> List[Carrier]:
        """Return carriers for the pair; default carriers for any other pair."""

        origin = self._normalize_city(city_pair.from_city)
        destination = self._normalize_city(city_pair.to_city)

        carriers = _RULES.get((origin, destination))
        if carriers is None:
            carriers = _DEFAULT_CARRIERS

        # Return a fresh list (entities are frozen, so the items are safe to
        # share, but the list itself should not be the shared rule object).
        return list(carriers)
