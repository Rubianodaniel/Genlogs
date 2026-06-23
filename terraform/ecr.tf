# Container registry for the backend image.
resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # allow `terraform destroy` to remove the repo + images

  image_scanning_configuration {
    scan_on_push = false
  }
}

# Optionally build the backend image and push it to ECR (needs Docker locally).
resource "null_resource" "backend_image" {
  count = var.build_and_push_image ? 1 : 0

  triggers = {
    repo = aws_ecr_repository.backend.repository_url
    tag  = var.backend_image_tag
  }

  provisioner "local-exec" {
    interpreter = ["bash", "-c"]
    command     = <<-EOT
      set -euo pipefail
      aws ecr get-login-password --region ${var.aws_region} \
        | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
      docker build --platform linux/amd64 \
        -t ${aws_ecr_repository.backend.repository_url}:${var.backend_image_tag} \
        ${path.module}/../backend
      docker push ${aws_ecr_repository.backend.repository_url}:${var.backend_image_tag}
    EOT
  }
}
