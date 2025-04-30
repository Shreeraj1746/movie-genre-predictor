variable "aws_region" {
  description = "The AWS region to deploy resources to"
  type        = string
  default     = "us-east-1" # Change as needed
}

variable "my_ip_cidr" {
  description = "Your IP address in CIDR notation for SSH access (e.g., 'your-ip/32')"
  type        = string
  default     = "0.0.0.0/0" # IMPORTANT: Change this to your IP address for security
}

variable "ami_id" {
  description = "The AMI ID to use for the EC2 instance"
  type        = string
  default     = "ami-0230bd60aa48260c6" # Amazon Linux 2023 in us-east-1
}

variable "key_name" {
  description = "Name of the SSH key pair to use for the EC2 instance"
  type        = string
}

variable "github_username" {
  description = "Your GitHub username for cloning the repository"
  type        = string
}
