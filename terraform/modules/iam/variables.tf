variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
}

variable "s3_bucket" {
  description = "Name of the S3 bucket to grant access to"
  type        = string
}
