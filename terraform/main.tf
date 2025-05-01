provider "aws" {
  region = var.aws_region
  profile = var.aws_profile
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

# VPC for our application
module "vpc" {
  source = "./modules/vpc"

  app_name        = var.app_name
  vpc_cidr        = var.vpc_cidr
  public_subnets  = var.public_subnets
  environment     = var.environment
}

# S3 bucket for application artifacts
module "s3" {
  source = "./modules/s3"

  app_name    = var.app_name
  environment = var.environment
}

# IAM roles and policies
module "iam" {
  source = "./modules/iam"

  app_name    = var.app_name
  environment = var.environment
  s3_bucket   = module.s3.bucket_name
}

# EC2 instance for application deployment
module "ec2" {
  source = "./modules/ec2"

  app_name        = var.app_name
  environment     = var.environment
  instance_type   = var.instance_type
  vpc_id          = module.vpc.vpc_id
  subnet_id       = module.vpc.public_subnet_ids[0]
  iam_role        = module.iam.ec2_profile_name
  s3_bucket       = module.s3.bucket_name
  key_name        = var.key_name
  user_data       = templatefile("${path.module}/templates/user_data.sh", {
    app_name    = var.app_name
    environment = var.environment
    region      = var.aws_region
    bucket_name = module.s3.bucket_name
    LOGFILE     = "/var/log/user-data.log"
  })
}

# Output the application endpoint
output "app_endpoint" {
  value       = "http://${module.ec2.public_ip}:8000"
  description = "The endpoint URL for the movie genre predictor API"
}

# Output the instance ID for debugging
output "instance_id" {
  value       = module.ec2.instance_id
  description = "The ID of the EC2 instance"
}

# Output the AWS region
output "aws_region" {
  value       = var.aws_region
  description = "The AWS region where resources are deployed"
}
