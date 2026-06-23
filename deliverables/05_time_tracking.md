# Point 5 — Time tracking (estimated vs actual)

> The hiring manager (John) asked to compare **estimated effort** against
> **actual effort**, expecting AI-assisted implementation to come in lower.
> This file is updated as each phase is completed.

## Status

- **Plan approved:** yes (John, after the point-1 email).
- **Go-ahead received:** yes — implementation started.

## Estimate vs actual

| Phase                              | Estimated | Actual | Notes |
|------------------------------------|-----------|--------|-------|
| Architecture & DB design (pts 2,3) | ~2h       | ~1h    | AI-drafted from the spec |
| Backend (FastAPI) + tests (4b)     | ~2h       | ~1h    | Clean Arch + TDD, AI-assisted |
| Frontend (React + Google Maps)(4a) | ~4h       | ~1h    | FSD scaffold generated, then refined |
| Deployment to cloud (4e)           | ~2h       | ~2.5h  | AWS App Runner + S3/CloudFront + Terraform; extra time on new-account friction (Free plan blocks App Runner → upgrade to paid) |
| Repo, prompts/rules, docs (4c,4d)  | ~1h       | ~0.5h  | |
| **Total**                          | **~11h**  | **~6h** | Hands-on; wall-clock longer only due to waiting on AWS account activation |

## Final note (to send to the interviewer at the end)

> Total actual hands-on time was **~6 hours** vs the **~11h** estimate. The
> difference is mainly AI-assisted scaffolding and code generation (backend and
> frontend came in well under estimate). Deployment ran slightly over its 2h
> estimate due to AWS new-account friction: the account started on the Free plan,
> which blocks App Runner, so it had to be upgraded to the paid plan. Calendar
> time spanned several days only because of waiting on AWS account activation, not
> active work.
