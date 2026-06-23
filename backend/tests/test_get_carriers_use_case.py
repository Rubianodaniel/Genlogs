"""Unit tests for ``GetCarriersUseCase`` in isolation.

The use case is exercised with a MOCK/fake ``CarrierRepository`` injected via
the constructor (DI). The real repository is never used here, so this verifies
orchestration only: the use case must query the port with the right city pair
and echo the original city strings alongside whatever the repo returns.
"""

from __future__ import annotations

from typing import List
from unittest.mock import MagicMock

from app.application.get_carriers import GetCarriersResult, GetCarriersUseCase
from app.domain.entities import Carrier, CityPair
from app.domain.ports import CarrierRepository


class _FakeRepo(CarrierRepository):
    """Hand-written fake recording the last queried pair."""

    def __init__(self, carriers: List[Carrier]) -> None:
        self._carriers = carriers
        self.last_pair: CityPair | None = None

    def find_by_city_pair(self, city_pair: CityPair) -> List[Carrier]:
        self.last_pair = city_pair
        return self._carriers


def test_execute_queries_repository_with_city_pair() -> None:
    """The use case builds a CityPair and passes it to the port."""

    fake = _FakeRepo([Carrier(name="ACME", trucks_per_day=3)])
    use_case = GetCarriersUseCase(repository=fake)

    use_case.execute("Origin City", "Dest City")

    assert fake.last_pair == CityPair(from_city="Origin City", to_city="Dest City")


def test_execute_returns_repo_carriers_and_echoes_cities() -> None:
    """Result echoes the original cities and carries the repo's carriers."""

    expected = [
        Carrier(name="ACME", trucks_per_day=3),
        Carrier(name="Globex", trucks_per_day=1),
    ]
    use_case = GetCarriersUseCase(repository=_FakeRepo(expected))

    result = use_case.execute("From", "To")

    assert isinstance(result, GetCarriersResult)
    assert result.from_city == "From"
    assert result.to_city == "To"
    assert result.carriers == expected


def test_execute_uses_mock_repository_call_once() -> None:
    """Using unittest.mock: the port is called exactly once."""

    mock_repo = MagicMock(spec=CarrierRepository)
    mock_repo.find_by_city_pair.return_value = []
    use_case = GetCarriersUseCase(repository=mock_repo)

    result = use_case.execute("A", "B")

    mock_repo.find_by_city_pair.assert_called_once_with(
        CityPair(from_city="A", to_city="B")
    )
    assert result.carriers == []
