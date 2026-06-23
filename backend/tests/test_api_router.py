"""Unit tests for the interface layer (FastAPI router).

These are unit tests of the delivery layer, not integration tests through the
real data: the use case is overridden via ``app.dependency_overrides`` with a
fake. The router's job is only to call the use case and shape the DTO, so the
fake returns canned data and we assert the wiring + JSON shape.
"""

from __future__ import annotations

from typing import List

import pytest
from fastapi.testclient import TestClient

from app.application.get_carriers import GetCarriersResult, GetCarriersUseCase
from app.domain.entities import Carrier
from app.interface.deps import get_carriers_use_case
from app.main import create_app


class _FakeUseCase:
    """Fake use case recording calls and returning canned carriers."""

    def __init__(self, carriers: List[Carrier]) -> None:
        self._carriers = carriers
        self.calls: list[tuple[str, str]] = []

    def execute(self, from_city: str, to_city: str) -> GetCarriersResult:
        self.calls.append((from_city, to_city))
        return GetCarriersResult(
            from_city=from_city, to_city=to_city, carriers=self._carriers
        )


@pytest.fixture
def fake_use_case() -> _FakeUseCase:
    return _FakeUseCase([Carrier(name="Fake Carrier", trucks_per_day=42)])


@pytest.fixture
def client(fake_use_case: _FakeUseCase) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_carriers_use_case] = lambda: fake_use_case
    return TestClient(app)


def test_post_carriers_calls_use_case_and_shapes_response(
    client: TestClient, fake_use_case: _FakeUseCase
) -> None:
    """POST routes the body to the use case and serializes its result."""

    resp = client.post(
        "/carriers", json={"from_city": "From X", "to_city": "To Y"}
    )

    assert resp.status_code == 200
    assert resp.json() == {
        "from_city": "From X",
        "to_city": "To Y",
        "carriers": [{"name": "Fake Carrier", "trucks_per_day": 42}],
    }
    assert fake_use_case.calls == [("From X", "To Y")]


def test_get_carriers_uses_query_params(
    client: TestClient, fake_use_case: _FakeUseCase
) -> None:
    """GET routes query params to the use case."""

    resp = client.get(
        "/carriers", params={"from_city": "Query One", "to_city": "Query Two"}
    )

    assert resp.status_code == 200
    assert resp.json()["carriers"] == [
        {"name": "Fake Carrier", "trucks_per_day": 42}
    ]
    assert fake_use_case.calls == [("Query One", "Query Two")]


def test_post_carriers_missing_field_returns_422(client: TestClient) -> None:
    """Missing required body field is rejected by validation."""

    resp = client.post("/carriers", json={"from_city": "only-one"})
    assert resp.status_code == 422


def test_health(client: TestClient) -> None:
    """Health probe returns ok."""

    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_default_wiring_resolves_use_case() -> None:
    """Smoke check that the real composition root builds a use case.

    No dependency override here: the default provider must return a usable
    ``GetCarriersUseCase`` (Factory + Singleton repo wiring is intact).
    """

    use_case = get_carriers_use_case()
    assert isinstance(use_case, GetCarriersUseCase)
