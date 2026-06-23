# Frontend → S3 + CloudFront (static SPA)

Builds `frontend/dist/` and serves it over an HTTPS CDN. Satisfies spec 004 §4.3
(F1–F4). The repeatable path is `deploy/frontend-deploy.sh`; this doc gives the
one-time infrastructure setup plus the manual equivalent of the script.

## Prerequisites

- AWS CLI v2 configured.
- Node 18+ / npm (to run `npm run build`).
- The **backend already deployed** (you need its App Runner URL for the build).
- A Google Maps API key whose HTTP-referrer restriction includes the CloudFront
  domain (see "Google Maps key" below — F2/G2).

## 1. One-time infrastructure

```bash
export AWS_REGION=us-east-1
export S3_BUCKET=genlogs-frontend           # must be globally unique

# Bucket (private; CloudFront reaches it via Origin Access Control).
aws s3api create-bucket --bucket "$S3_BUCKET" --region "$AWS_REGION"
aws s3api put-public-access-block --bucket "$S3_BUCKET" \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

Create the **CloudFront distribution** (console is simplest):

- Origin: the S3 bucket, using **Origin Access Control (OAC)** (recommended) so
  the bucket stays private. CloudFront then gives you a bucket-policy snippet to
  apply.
- **Default root object:** `index.html`.
- Viewer protocol policy: Redirect HTTP → HTTPS.
- **Custom error responses (F4 — SPA routing):** add two entries so client-side
  routes resolve to the app instead of S3's XML errors:

  | HTTP error code | Response page path | HTTP response code | TTL |
  | --------------- | ------------------ | ------------------ | --- |
  | 403             | `/index.html`      | 200                | 0   |
  | 404             | `/index.html`      | 200                | 0   |

  (403 matters because a private S3 + OAC origin returns 403, not 404, for
  missing keys.)

Record the **Distribution ID** (e.g. `E123ABC`) and the **domain**
(e.g. `d1234abcd.cloudfront.net`).

## 2. Build + upload (every deploy)

Use the script (preferred):

```bash
S3_BUCKET=genlogs-frontend \
CLOUDFRONT_DISTRIBUTION_ID=E123ABC \
VITE_API_BASE_URL=https://xxxx.us-east-1.awsapprunner.com \
VITE_GOOGLE_MAPS_API_KEY=AIza... \
  ./deploy/frontend-deploy.sh
```

Manual equivalent:

```bash
cd frontend
VITE_API_BASE_URL=https://xxxx.us-east-1.awsapprunner.com \
VITE_GOOGLE_MAPS_API_KEY=AIza... \
  npm run build

aws s3 sync dist/ s3://genlogs-frontend --delete \
  --exclude index.html --cache-control "public, max-age=31536000, immutable"
aws s3 cp dist/index.html s3://genlogs-frontend/index.html --cache-control "no-cache"

aws cloudfront create-invalidation --distribution-id E123ABC --paths "/*"
```

## Google Maps key (F2 / G2)

The Maps JS / Places / Directions key must allow the **CloudFront origin** as an
HTTP referrer. A localhost-only restriction will silently fail in production
(maps won't render). In Google Cloud Console → Credentials → your key →
Application restrictions → HTTP referrers, add:

```
https://d1234abcd.cloudfront.net/*
```

(Keep `http://localhost:5173/*` for local dev.)

## Verify

- Open `https://<cloudfront-domain>` — the portal loads.
- Deep-link a non-root path (if any) — still loads the app (F4 working).
- Search a corridor — carriers come back from the App Runner backend (confirms
  `VITE_API_BASE_URL` and backend `CORS_ORIGINS` are aligned).
