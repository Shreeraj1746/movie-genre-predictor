variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnets" {
  description = "CIDR blocks for the public subnets"
  type        = list(string)
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
}
