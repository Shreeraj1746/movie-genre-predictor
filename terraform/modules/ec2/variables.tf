variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "subnet_id" {
  description = "ID of the subnet to launch the instance in"
  type        = string
}

variable "key_name" {
  description = "Name of the SSH key pair to use for the EC2 instance"
  type        = string
  default     = null
}

variable "user_data" {
  description = "User data script for EC2 instance"
  type        = string
  default     = null
}

variable "iam_role" {
  description = "Name of the IAM instance profile to attach to the instance"
  type        = string
}

variable "s3_bucket" {
  description = "Name of the S3 bucket to use for application data"
  type        = string
}
