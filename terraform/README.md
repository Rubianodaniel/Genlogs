# Terraform — Genlogs AWS infrastructure

Spin the whole deployment up or down with one command:

- **Backend:** ECR repo + image + IAM role + **App Runner** service.
- **Frontend:** private **S3** bucket + **CloudFront** (OAC, SPA 403/404 → index.html).

This mirrors the manual steps in `../deploy/` as code, so the environment is
reproducible and **fully destroyable** (no leftover paid resources).

## Prerequisites

- Terraform >= 1.5
- AWS CLI v2 configured (`aws configure`) with permissions for ECR, App Runner,
  IAM, S3 and CloudFront.
- Docker (only if `build_and_push_image = true`, the default).
- Node 18+/npm (only if you pass `google_maps_api_key` so Terraform also builds
  and uploads the frontend).
- The AWS account must be on the **paid plan** — the Free plan blocks App Runner
  (`SubscriptionRequiredException`).

## Usage

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # edit values

terraform init
terraform apply                                # creates everything
```

To also build + upload the SPA in the same apply, set `google_maps_api_key` in
`terraform.tfvars` (the key must allow the CloudFront domain as an HTTP referrer —
but that domain only exists after the first apply, so a typical flow is:
`apply` infra → add the CloudFront domain to the Maps key → `apply` again with the
key set, or just run `../deploy/frontend-deploy.sh` with the outputs).

### Outputs

```bash
terraform output backend_url      # https://xxxx.us-east-1.awsapprunner.com
terraform output frontend_url     # https://xxxx.cloudfront.net
```

## Tear it down (stop all costs)

```bash
terraform destroy
```

Removes the App Runner service (the only real cost), CloudFront, S3 (emptied via
`force_destroy`), the ECR repo + images (`force_delete`), and the IAM role. After
this your AWS spend for the project returns to ~$0.

## Already created these resources manually?

This session provisioned the stack by hand first, so the names may already exist
in the account. A fresh `apply` would then fail with "already exists". Two options:

**A) Clean slate (simplest):** delete the manual resources, then `apply`.

```bash
aws apprunner delete-service --service-arn <arn>        # see ../progress/deploy_state.md
aws ecr delete-repository --repository-name genlogs-backend --force
aws s3 rb s3://genlogs-frontend-<account-id> --force
aws cloudfront delete-distribution --id <id> --if-match <etag>   # disable first
```

**B) Adopt them (import into state)** so Terraform manages the existing ones:

```bash
terraform import aws_ecr_repository.backend genlogs-backend
terraform import aws_iam_role.apprunner_ecr genlogs-AppRunnerECRAccessRole
terraform import aws_s3_bucket.frontend genlogs-frontend-<account-id>
terraform import aws_cloudfront_distribution.frontend <distribution-id>
terraform import aws_apprunner_service.backend <service-arn>
# (the manual IAM role was named "AppRunnerECRAccessRole"; this config uses
#  "genlogs-AppRunnerECRAccessRole", so importing is optional — a new one is fine.)
```

> Note the manually-created CloudFront domain (`dczrea1xzgt8g.cloudfront.net`) and
> App Runner URL differ from whatever a fresh `apply` produces. Update the Google
> Maps key referrer and any shared links if you recreate from scratch.

## Notes

- State is local (`terraform.tfstate`) and **gitignored**. For team use, switch to
  an S3 + DynamoDB backend.
- `terraform.tfvars` is gitignored (it can hold the Maps key).
