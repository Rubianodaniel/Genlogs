# Deploying Genlogs to AWS

This directory holds everything needed to deploy the Genlogs portal. Topology
(decided in `specs/004-deploy.md`):

- **Backend (FastAPI)** → container image → **AWS App Runner** (HTTPS, autoscaled).
- **Frontend (React/Vite)** → static `dist/` → **S3 + CloudFront** (HTTPS CDN).

| Artifact                          | Purpose                                            |
| --------------------------------- | -------------------------------------------------- |
| `../backend/Dockerfile`           | Builds the backend image (non-root, `$PORT`-aware) |
| `../backend/.dockerignore`        | Keeps the build context lean                       |
| `backend-apprunner.md`            | App Runner service setup (ECR push, port, health)  |
| `apprunner.yaml`                  | Documented App Runner settings                      |
| `frontend-s3-cloudfront.md`       | One-time S3/CloudFront setup + manual deploy steps |
| `frontend-deploy.sh`              | Repeatable build → S3 sync → CloudFront invalidate  |

## Prerequisites

- An **AWS account** and AWS CLI v2 configured (`aws configure`) with permissions
  for ECR, App Runner, S3 and CloudFront.
- **Docker** installed (to build/push the backend image).
- **Node 18+ / npm** (to build the frontend).
- A **Google Maps API key** (Maps JS + Places + Directions enabled) whose
  referrer restriction will include the **CloudFront domain** — see step 4.

## Order of operations

The frontend build needs the backend's live URL, so deploy the backend first.

1. **Deploy the backend** → follow `backend-apprunner.md` (build image, push to
   ECR, create the App Runner service with `CORS_ORIGINS` and health check
   `/health`). Note the resulting URL:
   `https://xxxx.<region>.awsapprunner.com`.

2. **Provision the frontend infra** (once) → follow `frontend-s3-cloudfront.md`
   step 1 (S3 bucket + CloudFront distribution, including the **SPA error
   responses 403/404 → `/index.html`**). Note the Distribution ID and CloudFront
   domain.

3. **Build + upload the frontend** with the backend URL baked in:

   ```bash
   S3_BUCKET=genlogs-frontend \
   CLOUDFRONT_DISTRIBUTION_ID=E123ABC \
   VITE_API_BASE_URL=https://xxxx.<region>.awsapprunner.com \
   VITE_GOOGLE_MAPS_API_KEY=AIza... \
     ./deploy/frontend-deploy.sh
   ```

4. **Update the Google Maps key restriction** → add the CloudFront origin
   (`https://<cloudfront-domain>/*`) to the key's HTTP-referrer allow-list in
   Google Cloud Console. **A localhost-only restriction will not work in
   production** — the maps will silently fail to render until this is done.

5. **Point the backend's CORS at CloudFront** → set `CORS_ORIGINS` on the App
   Runner service to the CloudFront URL and redeploy (see `backend-apprunner.md`
   step 4). The backend reads this from env; no code change.

## Live URLs (fill in after deploying)

> Paste the two final URLs here once the deploy is done.

- **Backend (App Runner):** `https://__REPLACE_ME__.awsapprunner.com`
- **Frontend (CloudFront):** `https://__REPLACE_ME__.cloudfront.net`

## Verifying

```bash
curl -s https://<app-runner-url>/health        # -> {"status":"ok"}
```

Then open the CloudFront URL, search a corridor, and confirm carriers load and
the map renders.

## Notes / future work

- No CI/CD pipeline is included (out of scope for the assessment). A natural next
  step is a GitHub Actions workflow that runs these same commands on push.
- The actual AWS `apply` (running these steps with real credentials) is performed
  by the repo owner; the artifacts here are correct and runnable.
