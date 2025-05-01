#!/bin/bash
set -e

# Script to deploy the movie genre predictor infrastructure to AWS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TERRAFORM_DIR="${PROJECT_DIR}/terraform"

echo "=== Deploying Movie Genre Predictor Infrastructure ==="
echo "Using Terraform configuration in: ${TERRAFORM_DIR}"

# Initialize and validate Terraform
cd "${TERRAFORM_DIR}"
terraform init
terraform validate

# Apply Terraform configuration
echo "Applying Terraform configuration..."
terraform apply -auto-approve

# Get the application endpoint
APP_ENDPOINT=$(terraform output -raw app_endpoint)

echo "=== Deployment Complete ==="
echo "Application endpoint: ${APP_ENDPOINT}"
echo "Run './scripts/test.sh' to test the application"
