"""Unit tests for the ``InMemoryCarrierRepo`` adapter.

Tests the repository directly (no HTTP, no use case): the three spec rule
cases plus case-insensitive / alias normalization.
"""

from __future__ import annotations

import pytest

from app.domain.entities import Carrier, CityPair
from app.infrastructure.in_memory_carrier_repo import InMemoryCarrierRepo


@pytest.fixture
def repo() -> InMemoryCarrierRepo:
    return InMemoryCarrierRepo()


def _find(repo: InMemoryCarrierRepo, frm: str, to: str) -> list[Carrier]:
    return repo.find_by_city_pair(CityPair(from_city=frm, to_city=to))


def test_rule_1_nyc_to_washington_dc(repo: InMemoryCarrierRepo) -> None:
    """Rule 1: New York City -> Washington DC (verbatim spec data)."""

    assert _find(repo, "New York City", "Washington DC") == [
        Carrier(name="Knight-Swift Transport Services", trucks_per_day=10),
        Carrier(name="J.B. Hunt Transport Services Inc", trucks_per_day=7),
        Carrier(name="YRC Worldwide", trucks_per_day=5),
    ]


def test_rule_2_sf_to_la(repo: InMemoryCarrierRepo) -> None:
    """Rule 2: San Francisco -> Los Angeles (verbatim spec data)."""

    assert _find(repo, "San Francisco", "Los Angeles") == [
        Carrier(name="XPO Logistics", trucks_per_day=9),
        Carrier(name="Schneider", trucks_per_day=6),
        Carrier(name="Landstar Systems", trucks_per_day=2),
    ]


def test_rule_3_other_pair_returns_default(repo: InMemoryCarrierRepo) -> None:
    """Rule 3: any other pair returns the default carriers."""

    assert _find(repo, "Chicago", "Houston") == [
        Carrier(name="UPS Inc.", trucks_per_day=11),
        Carrier(name="FedEx Corp", trucks_per_day=9),
    ]


@pytest.mark.parametrize(
    "frm,to",
    [
        ("nyc", "washington"),
        ("NYC", "DC"),
        ("  New York ", "washington d.c."),
    ],
)
def test_alias_variants_resolve_to_rule_1(
    repo: InMemoryCarrierRepo, frm: str, to: str
) -> None:
    """Aliases / casing / whitespace resolve to rule 1."""

    result = _find(repo, frm, to)
    assert result[0] == Carrier(
        name="Knight-Swift Transport Services", trucks_per_day=10
    )
    assert len(result) == 3


@pytest.mark.parametrize(
    "frm,to",
    [
        ("SF", "LA"),
        ("  SF ", "la"),
        ("san francisco", "Los Angeles"),
    ],
)
def test_alias_variants_resolve_to_rule_2(
    repo: InMemoryCarrierRepo, frm: str, to: str
) -> None:
    """Aliases / casing / whitespace resolve to rule 2."""

    result = _find(repo, frm, to)
    assert result[0] == Carrier(name="XPO Logistics", trucks_per_day=9)
    assert len(result) == 3


def test_returned_list_is_not_shared_rule_object(repo: InMemoryCarrierRepo) -> None:
    """Mutating a returned list must not affect later lookups."""

    first = _find(repo, "New York City", "Washington DC")
    first.clear()
    second = _find(repo, "New York City", "Washington DC")
    assert len(second) == 3
