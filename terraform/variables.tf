variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS profile to use for credentials"
  type        = string
  default     = "default"
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "movie-genre-predictor"
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  default     = "test"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "CIDR blocks for the public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro" # Free tier eligible
}

variable "key_name" {
  description = "Name of the SSH keypair to use for EC2 instance"
  type        = string
  default     = null
}
