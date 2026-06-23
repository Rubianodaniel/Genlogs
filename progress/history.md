# History (append-only)

> Append-only log of finished sessions. Newest at the bottom. At session close,
> move the `progress/current.md` summary here.

---

## 2026-06-23 — Feature 3 (deploy) live on AWS, verified & closed

- Backend FastAPI deployed to **AWS App Runner** (ECR image `genlogs-backend`):
  **https://cah82yetag.us-east-1.awsapprunner.com**, status RUNNING,
  `CORS_ORIGINS=https://dczrea1xzgt8g.cloudfront.net`.
- Frontend (Vite build, `VITE_API_BASE_URL` → App Runner URL) on **S3 +
  CloudFront**: **https://dczrea1xzgt8g.cloudfront.net** (SPA 403/404 →
  /index.html).
- **Root cause of the earlier deploy block:** account was on the new **Free
  account plan**, which disallows App Runner (`SubscriptionRequiredException`).
  Fixed by **Upgrade plan** → paid (pay-as-you-go; ~$100 credits cover it).
- Independent verification (curl): `/health` → `{"status":"ok"}` (200);
  `POST /carriers` SF→LA → XPO Logistics (9), Schneider (6), Landstar Systems (2)
  with `Access-Control-Allow-Origin: https://dczrea1xzgt8g.cloudfront.net`;
  CloudFront `/` → HTTP 200 text/html. All passed → feature 3 marked `done`.
- All features (1–4) now `done`. Cleanup commands to stop AWS costs are in
  `progress/deploy_state.md`.
