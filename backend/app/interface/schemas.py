"""Pydantic request/response DTOs for the carriers endpoint.

These belong to the delivery layer only; the domain stays framework-free.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from app.application.get_carriers import GetCarriersResult


class CarriersRequest(BaseModel):
    """Request body for the carriers endpoint."""

    from_city: str = Field(..., description="Origin city")
    to_city: str = Field(..., description="Destination city")


class CarrierOut(BaseModel):
    """A single carrier in the response."""

    name: str
    trucks_per_day: int


class CarriersResponse(BaseModel):
    """Response body for the carriers endpoint."""

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
