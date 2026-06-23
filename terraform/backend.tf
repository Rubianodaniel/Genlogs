# Backend (FastAPI) running on AWS App Runner from the ECR image.
resource "aws_apprunner_service" "backend" {
  service_name = "${var.project_name}-backend"

  source_configuration {
    auto_deployments_enabled = false

    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.backend.repository_url}:${var.backend_image_tag}"
      image_repository_type = "ECR"

      image_configuration {
        port = var.backend_port

        # CORS origin = the CloudFront domain (resolved at apply time, no cycle:
        # backend -> cloudfront -> s3). The app reads CORS_ORIGINS from env.
        runtime_environment_variables = {
          CORS_ORIGINS = "https://${aws_cloudfront_distribution.frontend.domain_name}"
        }
      }
    }
  }

  instance_configuration {
    cpu    = "0.25 vCPU"
    memory = "0.5 GB"
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  depends_on = [
    aws_iam_role_policy_attachment.apprunner_ecr,
    null_resource.backend_image,
  ]
}
