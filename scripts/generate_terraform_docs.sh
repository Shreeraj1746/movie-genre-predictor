#!/bin/bash

# Script to generate terraform documentation for all modules

set -e

# Check if terraform-docs is installed
if ! command -v terraform-docs &> /dev/null; then
    echo "terraform-docs is not installed. Please install it first:"
    echo "  macOS: brew install terraform-docs"
    echo "  Others: Visit https://terraform-docs.io/user-guide/installation/"
    exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${ROOT_DIR}/.terraform-docs.yml"
TERRAFORM_DIR="${ROOT_DIR}/terraform"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: terraform-docs config file not found at ${CONFIG_FILE}"
    exit 1
fi

echo "Generating documentation for main Terraform directory..."
# Go to the terraform directory and run terraform-docs
cd "$TERRAFORM_DIR" && terraform-docs --config "$ROOT_DIR/.terraform-docs.yml" .

# Process each module
for MODULE_DIR in "${TERRAFORM_DIR}/modules"/*; do
    if [ -d "$MODULE_DIR" ]; then
        MODULE_NAME=$(basename "$MODULE_DIR")
        echo "Generating documentation for module: ${MODULE_NAME}"
        # Go to the module directory and run terraform-docs
        cd "$MODULE_DIR" && terraform-docs --config "$ROOT_DIR/.terraform-docs.yml" .
    fi
done

echo "Documentation generation complete!"
