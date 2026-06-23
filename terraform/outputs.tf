output "backend_url" {
  description = "Live backend (App Runner) HTTPS URL."
  value       = "https://${aws_apprunner_service.backend.service_url}"
}

output "frontend_url" {
  description = "Live frontend (CloudFront) HTTPS URL."
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "s3_bucket" {
  description = "Frontend S3 bucket name (target for deploy/frontend-deploy.sh)."
  value       = aws_s3_bucket.frontend.bucket
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution id (for cache invalidations)."
  value       = aws_cloudfront_distribution.frontend.id
}

output "ecr_repository_url" {
  description = "ECR repository URL for the backend image."
  value       = aws_ecr_repository.backend.repository_url
}
