# Spec 003 — Backend input/output validation (Pydantic) + security hardening

## Goal

Harden the carriers API so that **everything entering and leaving** the app is
strictly validated with Pydantic, and add baseline security. Behavior of the
carrier rules (spec 001) must not change — this only adds validation, safer
errors, and security middleware.

## 3.1 Input validation (DTOs)

`CarriersRequest` (POST body) and the GET query params must both enforce:

- `from_city` / `to_city`:
  - **required**, type `str`.
  - `strip_whitespace=True`, `min_length=1` after trim (reject empty / whitespace-only).
  - `max_length=100` (reject oversized input → DoS / abuse).
  - **allowed-character pattern**: letters (incl. accents), spaces, and `. , ' -`
    only. Reject digits-only and control/injection characters
    (e.g. `<`, `>`, `;`, `{`, `}`, `\`, backticks, null bytes).
- `model_config = ConfigDict(extra="forbid")` → reject unexpected/extra fields.
- The GET endpoint validates its query params with the **same** constraints
  (shared validator or a `Query(..., min_length=1, max_length=100, pattern=...)`
  dependency) — no unvalidated path into the use case.

> DRY: define the field constraints once (a reusable `CityField` /
> `Annotated[str, ...]` type or a shared validator) and use it for body and query.

## 3.2 Output validation (DTOs)

- `CarrierOut`: `name: str`, `trucks_per_day: int` with `ge=0`.
- `CarriersResponse`: typed list; `extra="forbid"`. The route keeps
  `response_model=CarriersResponse` so the output is validated/serialized strictly.

## 3.3 Error handling (no information leakage)

- Pydantic/validation failures return **HTTP 422** with a clean, structured JSON
  body (`{"detail": [...]}`). Add a handler that returns a consistent shape and
  does **not** leak stack traces or internal details.
- Unhandled exceptions return a generic **HTTP 500** body (no traceback to client).

## 3.4 Security middleware & config

- **CORS hardening**: replace `allow_origins=["*"] + allow_credentials=True`
  (an insecure/invalid combo). Allowed origins come from configuration
  (`Settings.cors_origins`, env-driven), defaulting to local dev origins
  (`http://localhost:5173`, `http://localhost:3000`). Methods limited to
  `GET, POST, OPTIONS`.
- **Security headers** middleware on every response:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: no-referrer`
  - `Cache-Control: no-store` for API responses.
- **Settings** object (Singleton via `functools.lru_cache`) holds `cors_origins`
  and any limits, read from env vars — no secrets hardcoded.
- (Optional / future) request rate limiting — out of scope for this spec to keep
  it simple (KISS); noted as a follow-up.

## 3.5 Acceptance criteria

- [ ] Empty / whitespace-only city → 422 (not passed to the use case).
- [ ] City > 100 chars → 422.
- [ ] City with `<script>` / injection chars → 422.
- [ ] Extra/unexpected body field → 422.
- [ ] Invalid GET query params → 422 with the same rules as POST.
- [ ] Valid requests still return the exact spec-001 carriers (no regression).
- [ ] Response includes the security headers above.
- [ ] CORS reflects only configured origins (not `*`).
- [ ] Output is validated by `response_model`; `trucks_per_day >= 0`.
- [ ] All covered by pytest **unit** tests (mocks + DI), `./init.sh` green.
