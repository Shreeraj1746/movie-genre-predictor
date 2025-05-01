#!/bin/bash
set -e

# Script to destroy the AWS infrastructure

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TERRAFORM_DIR="${PROJECT_DIR}/terraform"

echo "=== Destroying Movie Genre Predictor Infrastructure ==="
echo "Using Terraform configuration in: ${TERRAFORM_DIR}"

# Destroy Terraform resources
cd "${TERRAFORM_DIR}"
terraform destroy -auto-approve

echo "=== Infrastructure Destroyed ==="
echo "All AWS resources have been removed."
