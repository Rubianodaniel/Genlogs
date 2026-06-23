# Deploy state (feature 3) — live AWS resources

> Running log of the actual AWS apply. Account `185818464819`, region `us-east-1`,
> IAM user `Daniel` (AdministratorAccess attached during this session).

## Done

- **ECR repo:** `genlogs-backend` → `185818464819.dkr.ecr.us-east-1.amazonaws.com/genlogs-backend`
  - Image pushed, tag `latest` (digest `sha256:2f4e625c8e...`).
- **IAM role:** `AppRunnerECRAccessRole` (trust `build.apprunner.amazonaws.com`,
  policy `AWSAppRunnerServicePolicyForECRAccess`) — lets App Runner pull from ECR.
- **S3 bucket (frontend):** `genlogs-frontend-185818464819` (private, public access
  blocked). Bucket policy allows the CloudFront distribution via OAC.
- **CloudFront OAC:** id `EKAY5NRCTSDQP`.
- **CloudFront distribution:** id `E3FU2IZGYR7ORG`, domain
  **`dczrea1xzgt8g.cloudfront.net`** (SPA error responses 403/404 → /index.html 200).
  Status InProgress at creation (~15 min to deploy).

## Blocked / pending

- **App Runner service** (`genlogs-backend`): blocked by
  `SubscriptionRequiredException` — the AWS account is brand-new and still
  activating (paid services not enabled yet). A background retry loop
  (`scratchpad/retry-apprunner.sh`, every 20 min) keeps attempting
  `create-service` with `CORS_ORIGINS=https://dczrea1xzgt8g.cloudfront.net`.
  Result will land in `scratchpad/apprunner-result.json`.

## Remaining steps (after backend is up)

1. Get App Runner URL (`aws apprunner list-services ...`).
2. Build frontend with `VITE_API_BASE_URL=<app-runner-url>` +
   `VITE_GOOGLE_MAPS_API_KEY=<key valid for CloudFront origin>`; upload to S3;
   invalidate CloudFront (`deploy/frontend-deploy.sh`).
3. Update Google Maps API key referrer restriction to include
   `https://dczrea1xzgt8g.cloudfront.net/*` (localhost-only fails in prod).
4. Verify `/health` on App Runner and the portal on CloudFront; paste both live
   URLs into `deploy/README.md`; only then mark feature 3 `done`.

## Cleanup (to stop costs after the assessment)

- `aws apprunner delete-service --service-arn <arn>` (the only real cost).
- Optionally delete CloudFront distribution + S3 bucket + ECR repo.
