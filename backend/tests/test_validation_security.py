"""Unit tests for spec 003 — input/output validation + security hardening.

These are unit tests of the delivery (interface) layer. Where the use case is
not the subject under test, it is overridden via ``app.dependency_overrides``
with a fake (DI seam). One no-regression test uses the real composition root to
prove spec-001 carriers are unchanged for a valid request.
"""

from __future__ import annotations

import os
from typing import List

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.application.get_carriers import GetCarriersResult
from app.domain.entities import Carrier
from app.interface.deps import get_carriers_use_case
from app.interface.schemas import CarrierOut, CarriersRequest
from app.interface.settings import Settings, get_settings
from app.main import _SECURITY_HEADERS, create_app


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
    """Client whose use case is the fake (interface-layer unit under test)."""

    app = create_app()
    app.dependency_overrides[get_carriers_use_case] = lambda: fake_use_case
    return TestClient(app)


# --------------------------------------------------------------------------- #
# 3.1 Input validation — POST body                                            #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("bad_city", ["", "   ", "\t", "\n  \n"])
def test_post_empty_or_whitespace_city_returns_422(
    client: TestClient, fake_use_case: _FakeUseCase, bad_city: str
) -> None:
    """Empty / whitespace-only city is rejected and never reaches the use case."""

    resp = client.post(
        "/carriers", json={"from_city": bad_city, "to_city": "Boston"}
    )

    assert resp.status_code == 422
    assert fake_use_case.calls == []


def test_post_oversized_city_returns_422(
    client: TestClient, fake_use_case: _FakeUseCase
) -> None:
    """City longer than 100 chars is rejected."""

    resp = client.post(
        "/carriers",
        json={"from_city": "A" * 101, "to_city": "Boston"},
    )

    assert resp.status_code == 422
    assert fake_use_case.calls == []


@pytest.mark.parametrize(
    "bad_city",
    [
        "<script>alert(1)</script>",
        "Boston; DROP TABLE",
        "City{evil}",
        "back`tick`",
        "back\\slash",
        "12345",  # digits-only
        "City2",  # contains a digit
    ],
)
def test_post_injection_or_invalid_chars_returns_422(
    client: TestClient, fake_use_case: _FakeUseCase, bad_city: str
) -> None:
    """Injection / disallowed characters and digits are rejected."""

    resp = client.post(
        "/carriers", json={"from_city": bad_city, "to_city": "Boston"}
    )

    assert resp.status_code == 422
    assert fake_use_case.calls == []


def test_post_extra_field_returns_422(
    client: TestClient, fake_use_case: _FakeUseCase
) -> None:
    """An unexpected extra body field is rejected (extra='forbid')."""

    resp = client.post(
        "/carriers",
        json={"from_city": "Boston", "to_city": "Albany", "evil": "x"},
    )

    assert resp.status_code == 422
    assert fake_use_case.calls == []


@pytest.mark.parametrize(
    "good_city",
    ["New York", "St. Louis", "Winston-Salem", "Coeur d'Alene", "Bogotá", "Zürich"],
)
def test_post_accepts_valid_city_names(
    client: TestClient, good_city: str
) -> None:
    """Valid names (accents, spaces, . , ' -) pass and round-trip trimmed."""

    resp = client.post(
        "/carriers", json={"from_city": f"  {good_city}  ", "to_city": "Boston"}
    )

    assert resp.status_code == 200
    # strip_whitespace trimmed the leading/trailing spaces before use.
    assert resp.json()["from_city"] == good_city


# --------------------------------------------------------------------------- #
# 3.1 Input validation — GET query params (same rules)                        #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "params",
    [
        {"from_city": "", "to_city": "Boston"},
        {"from_city": "   ", "to_city": "Boston"},
        {"from_city": "A" * 101, "to_city": "Boston"},
        {"from_city": "<script>", "to_city": "Boston"},
        {"from_city": "City2", "to_city": "Boston"},
        {"to_city": "Boston"},  # missing required from_city
    ],
)
def test_get_invalid_query_params_return_422(
    client: TestClient, fake_use_case: _FakeUseCase, params: dict
) -> None:
    """GET enforces the same constraints as POST; bad params → 422."""

    resp = client.get("/carriers", params=params)

    assert resp.status_code == 422
    assert fake_use_case.calls == []


def test_get_accepts_valid_query_params(
    client: TestClient, fake_use_case: _FakeUseCase
) -> None:
    """Valid GET params route through to the use case, trimmed."""

    resp = client.get(
        "/carriers", params={"from_city": "  New York  ", "to_city": "Boston"}
    )

    assert resp.status_code == 200
    assert fake_use_case.calls == [("New York", "Boston")]


# --------------------------------------------------------------------------- #
# 3.2 Output validation                                                       #
# --------------------------------------------------------------------------- #


def test_carrier_out_rejects_negative_trucks_per_day() -> None:
    """The output model enforces trucks_per_day >= 0."""

    with pytest.raises(ValidationError):
        CarrierOut(name="X", trucks_per_day=-1)


def test_carrier_out_accepts_zero_trucks_per_day() -> None:
    """Zero is a valid trucks_per_day value (ge=0)."""

    assert CarrierOut(name="X", trucks_per_day=0).trucks_per_day == 0


# --------------------------------------------------------------------------- #
# 3.3 Error handling (no info leakage)                                        #
# --------------------------------------------------------------------------- #


def test_validation_error_has_clean_detail_shape(client: TestClient) -> None:
    """422 bodies use the consistent {'detail': [...]} shape, no traceback."""

    resp = client.post("/carriers", json={"from_city": "", "to_city": "Boston"})

    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body
    assert "Traceback" not in resp.text


def test_unhandled_exception_returns_generic_500(
    fake_use_case: _FakeUseCase,
) -> None:
    """An unexpected error yields a generic 500 with no internal details."""

    class _BoomUseCase:
        def execute(self, from_city: str, to_city: str):
            raise RuntimeError("secret internal detail")

    app = create_app()
    app.dependency_overrides[get_carriers_use_case] = lambda: _BoomUseCase()
    # raise_server_exceptions=False so the registered handler runs (not pytest).
    boom_client = TestClient(app, raise_server_exceptions=False)

    resp = boom_client.post(
        "/carriers", json={"from_city": "Boston", "to_city": "Albany"}
    )

    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error."}
    assert "secret internal detail" not in resp.text
    assert "Traceback" not in resp.text


# --------------------------------------------------------------------------- #
# 3.4 Security middleware & config                                            #
# --------------------------------------------------------------------------- #


def test_responses_include_security_headers(client: TestClient) -> None:
    """Every response carries the baseline security headers."""

    resp = client.get("/health")

    for header, value in _SECURITY_HEADERS.items():
        assert resp.headers.get(header) == value


def test_settings_default_cors_origins(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings default to local dev origins when env is unset (Singleton)."""

    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert settings.cors_origins_list == [
            "http://localhost:5173",
            "http://localhost:3000",
        ]
        # Singleton: same cached instance returned.
        assert get_settings() is settings
    finally:
        get_settings.cache_clear()


def test_settings_reads_cors_origins_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CORS origins are parsed from the env var, trimming blanks."""

    monkeypatch.setenv(
        "CORS_ORIGINS", " https://app.example.com , https://admin.example.com ,"
    )
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert settings.cors_origins_list == [
            "https://app.example.com",
            "https://admin.example.com",
        ]
    finally:
        get_settings.cache_clear()


def test_cors_reflects_allowed_origin_only(
    monkeypatch: pytest.MonkeyPatch, fake_use_case: _FakeUseCase
) -> None:
    """An allowed origin is reflected; a disallowed one is not (never '*')."""

    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    get_settings.cache_clear()
    try:
        app = create_app()
        app.dependency_overrides[get_carriers_use_case] = lambda: fake_use_case
        cors_client = TestClient(app)

        allowed = cors_client.get(
            "/health", headers={"Origin": "http://localhost:5173"}
        )
        assert (
            allowed.headers.get("access-control-allow-origin")
            == "http://localhost:5173"
        )

        disallowed = cors_client.get(
            "/health", headers={"Origin": "http://evil.example.com"}
        )
        acao = disallowed.headers.get("access-control-allow-origin")
        assert acao != "*"
        assert acao != "http://evil.example.com"
    finally:
        get_settings.cache_clear()


# --------------------------------------------------------------------------- #
# 3.5 No regression — valid request still returns exact spec-001 carriers     #
# --------------------------------------------------------------------------- #


def test_valid_request_returns_spec_001_carriers_via_real_repo() -> None:
    """End-to-end through the real composition root: NYC -> DC unchanged."""

    app = create_app()  # no override: real use case + in-memory repo
    real_client = TestClient(app)

    resp = real_client.post(
        "/carriers", json={"from_city": "New York", "to_city": "Washington DC"}
    )

    assert resp.status_code == 200
    assert resp.json() == {
        "from_city": "New York",
        "to_city": "Washington DC",
        "carriers": [
            {"name": "Knight-Swift Transport Services", "trucks_per_day": 10},
            {"name": "J.B. Hunt Transport Services Inc", "trucks_per_day": 7},
            {"name": "YRC Worldwide", "trucks_per_day": 5},
        ],
    }


def test_carriers_request_model_forbids_extra_directly() -> None:
    """Direct model check: extra fields raise (extra='forbid')."""

    with pytest.raises(ValidationError):
        CarriersRequest(from_city="Boston", to_city="Albany", extra="x")
