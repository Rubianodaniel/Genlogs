variable "aws_region" {
  description = "AWS region for all resources (App Runner + ECR + S3). CloudFront is global."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefix used for resource names."
  type        = string
  default     = "genlogs"
}

variable "backend_image_tag" {
  description = "Tag of the backend container image in ECR."
  type        = string
  default     = "latest"
}

variable "backend_port" {
  description = "Port the FastAPI container listens on (App Runner routes to it)."
  type        = string
  default     = "8000"
}

variable "build_and_push_image" {
  description = <<-EOT
    If true, Terraform builds the backend Docker image from ../backend and pushes
    it to ECR during apply (requires Docker + AWS CLI on the machine running
    Terraform). Set to false if the image is already in ECR.
  EOT
  type        = bool
  default     = true
}

variable "google_maps_api_key" {
  description = <<-EOT
    Google Maps JS API key used to build the frontend. If non-empty, Terraform
    runs ../deploy/frontend-deploy.sh during apply to build + upload the SPA. If
    empty, only the infrastructure is provisioned (run the script yourself later).
  EOT
  type        = string
  default     = ""
  sensitive   = true
}
