# Backend → AWS App Runner (image-based)

Deploys `backend/` as a container on App Runner. App Runner gives an HTTPS URL,
autoscales, and needs no VPC/ALB. Satisfies spec 004 §4.2 (D1–D7).

## Service settings (the contract)

| Setting            | Value                                                        |
| ------------------ | ----------------------------------------------------------- |
| Source             | Container image in **ECR** (built from `backend/Dockerfile`) |
| Port               | `8000` (the container also honours injected `PORT`)         |
| Health check       | Protocol **HTTP**, path **`/health`** → 200 `{"status":"ok"}` |
| Start command      | from the image (`uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`) |
| Env var            | `CORS_ORIGINS` = the CloudFront origin(s), comma-separated  |
| CPU / Memory       | 0.25 vCPU / 0.5 GB is plenty for this assessment            |

> **CORS (D7):** the backend reads `CORS_ORIGINS` from the environment
> (`backend/app/interface/settings.py`). It MUST include the CloudFront URL of the
> deployed frontend, e.g. `https://d1234abcd.cloudfront.net`. No code change is
> needed — this is purely an env var on the App Runner service. You can set it now
> with a placeholder and update it once CloudFront exists (then the service
> redeploys).

## Prerequisites

- AWS CLI v2 configured (`aws configure`) with an account that can use ECR + App Runner.
- Docker installed (to build/push the image).
- An ECR repository (create once): `aws ecr create-repository --repository-name genlogs-backend`.

Set shell variables (adjust region/account):

```bash
export AWS_REGION=us-east-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REPO=genlogs-backend
export IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest"
```

## 1. Build and push the image

Run from the repo root (build context is `backend/`):

```bash
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

docker build -t "$ECR_REPO" backend/
docker tag "$ECR_REPO:latest" "$IMAGE_URI"
docker push "$IMAGE_URI"
```

## 2. Create the App Runner service

Easiest via the **console**: Create service → Source = Container registry → pick
the ECR image → Port `8000` → Health check path `/health` → Env var
`CORS_ORIGINS=https://<cloudfront-domain>` → Create.

Or via CLI (an `access-role-arn` that lets App Runner pull from ECR is required):

```bash
aws apprunner create-service \
  --service-name genlogs-backend \
  --source-configuration '{
    "AuthenticationConfiguration": {"AccessRoleArn": "arn:aws:iam::'"$ACCOUNT_ID"':role/AppRunnerECRAccessRole"},
    "ImageRepository": {
      "ImageIdentifier": "'"$IMAGE_URI"'",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {"CORS_ORIGINS": "https://REPLACE_WITH_CLOUDFRONT_DOMAIN"}
      }
    }
  }' \
  --health-check-configuration '{"Protocol": "HTTP", "Path": "/health", "Interval": 10, "Timeout": 5, "HealthyThreshold": 1, "UnhealthyThreshold": 5}' \
  --instance-configuration '{"Cpu": "0.25 vCPU", "Memory": "0.5 GB"}'
```

## 3. Grab the URL

```bash
aws apprunner list-services \
  --query "ServiceSummaryList[?ServiceName=='genlogs-backend'].ServiceUrl" --output text
```

That `https://xxxx.<region>.awsapprunner.com` is the **backend live URL**. Paste it
into `deploy/README.md` and use it as `VITE_API_BASE_URL` for the frontend build.

## 4. Updating CORS after the frontend exists

Once CloudFront is live, set `CORS_ORIGINS` to its URL and trigger a deployment:

```bash
aws apprunner update-service --service-arn <service-arn> \
  --source-configuration '{"ImageRepository":{"ImageIdentifier":"'"$IMAGE_URI"'","ImageRepositoryType":"ECR","ImageConfiguration":{"Port":"8000","RuntimeEnvironmentVariables":{"CORS_ORIGINS":"https://<cloudfront-domain>"}}}}'
```

## Verify

```bash
curl -s https://xxxx.<region>.awsapprunner.com/health   # -> {"status":"ok"}
```
