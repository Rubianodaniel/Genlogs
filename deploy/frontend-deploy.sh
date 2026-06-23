#!/usr/bin/env bash
# Frontend deploy: build + upload to S3 + invalidate CloudFront.
# Satisfies spec 004 §4.3 (F1–F4). Run from the repo root.
#
# Required env vars:
#   S3_BUCKET                 target bucket name (e.g. genlogs-frontend)
#   CLOUDFRONT_DISTRIBUTION_ID  distribution to invalidate
#   VITE_API_BASE_URL         deployed App Runner URL (NOT localhost)
#   VITE_GOOGLE_MAPS_API_KEY  Maps key valid for the CloudFront origin
#
# Example:
#   S3_BUCKET=genlogs-frontend \
#   CLOUDFRONT_DISTRIBUTION_ID=E123ABC \
#   VITE_API_BASE_URL=https://xxxx.us-east-1.awsapprunner.com \
#   VITE_GOOGLE_MAPS_API_KEY=AIza... \
#   ./deploy/frontend-deploy.sh
set -euo pipefail

: "${S3_BUCKET:?Set S3_BUCKET}"
: "${CLOUDFRONT_DISTRIBUTION_ID:?Set CLOUDFRONT_DISTRIBUTION_ID}"
: "${VITE_API_BASE_URL:?Set VITE_API_BASE_URL (deployed backend URL, not localhost)}"
: "${VITE_GOOGLE_MAPS_API_KEY:?Set VITE_GOOGLE_MAPS_API_KEY}"

# Resolve repo root relative to this script so it runs from anywhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> Building frontend (Vite) with production env"
cd "$ROOT_DIR/frontend"
if [ ! -d node_modules ]; then
  npm ci
fi
# Vite inlines VITE_* vars at build time (F2).
VITE_API_BASE_URL="$VITE_API_BASE_URL" \
VITE_GOOGLE_MAPS_API_KEY="$VITE_GOOGLE_MAPS_API_KEY" \
  npm run build

echo "==> Syncing dist/ to s3://$S3_BUCKET"
# Long-cache the fingerprinted assets, but never cache index.html so new
# deploys are picked up immediately.
aws s3 sync dist/ "s3://$S3_BUCKET" --delete \
  --exclude "index.html" \
  --cache-control "public, max-age=31536000, immutable"
aws s3 cp dist/index.html "s3://$S3_BUCKET/index.html" \
  --cache-control "no-cache"

echo "==> Invalidating CloudFront ($CLOUDFRONT_DISTRIBUTION_ID)"
aws cloudfront create-invalidation \
  --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
  --paths "/*"

echo "==> Done. Frontend live at your CloudFront domain."
