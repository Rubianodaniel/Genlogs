"""Pydantic request/response DTOs for the carriers endpoint.

These belong to the delivery layer only; the domain stays framework-free. All
input and output crossing the API boundary is strictly validated here
(spec 003).
"""

from __future__ import annotations

from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.application.get_carriers import GetCarriersResult

# Allowed-character pattern for a city name:
#   - \p{L}  unicode letters (incl. accents like é, ñ, ü)
#   - \p{M}  combining marks (accents expressed as separate code points)
#   - space and the punctuation . , ' -
# Anything else (digits, <, >, ;, {, }, \\, backticks, control/null bytes) is
# rejected. Requiring at least one letter (the leading char class up front is
# permissive, so the pattern below also rejects digits-only / punctuation-only
# input by demanding the whole string match these classes only — combined with
# a separate "must contain a letter" check is overkill; the class set already
# excludes digits, so digits-only cannot match).
_CITY_PATTERN = r"^[\p{L}\p{M} .,'\-]+$"

# DRY: define the city field constraints ONCE and reuse for body + query params.
# ``strip_whitespace`` trims first, then min/max length and the pattern apply to
# the trimmed value, so whitespace-only input fails ``min_length=1``.
CityField = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
        pattern=_CITY_PATTERN,
    ),
]


class CarriersRequest(BaseModel):
    """Request body for the carriers endpoint.

    ``extra="forbid"`` rejects unexpected fields (anti-tampering / strictness).
    """

    model_config = ConfigDict(extra="forbid")

    from_city: CityField = Field(..., description="Origin city")
    to_city: CityField = Field(..., description="Destination city")


class CarrierOut(BaseModel):
    """A single carrier in the response."""

    model_config = ConfigDict(extra="forbid")

    name: str
    trucks_per_day: int = Field(..., ge=0)


class CarriersResponse(BaseModel):
    """Response body for the carriers endpoint."""

    model_config = ConfigDict(extra="forbid")

    from_city: str
    to_city: str
    carriers: List[CarrierOut]

    @classmethod
    def from_result(cls, result: GetCarriersResult) -> "CarriersResponse":
        """Build the response DTO from a use-case result."""

        return cls(
            from_city=result.from_city,
            to_city=result.to_city,
            carriers=[
                CarrierOut(name=c.name, trucks_per_day=c.trucks_per_day)
                for c in result.carriers
            ],
        )
