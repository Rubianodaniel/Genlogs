"""Domain entities for the carriers API.

Pure Python value objects with no dependency on FastAPI, HTTP or any
framework. See ``specs/001-carriers-api.md``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Carrier:
    """A carrier and the number of trucks it moves per day on a route."""

    name: str
    trucks_per_day: int


@dataclass(frozen=True)
class CityPair:
    """An origin/destination city pair as provided by the caller.

    Holds the raw strings exactly as received; normalization of variants and
    casing is the responsibility of the repository adapter, not the domain.
    """

    from_city: str
    to_city: str
