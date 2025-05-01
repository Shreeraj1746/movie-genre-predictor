#!/bin/bash
set -e

# This script orchestrates the complete deployment, testing, and cleanup process
# for the Movie Genre Predictor application on AWS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Movie Genre Predictor AWS Deployment Pipeline ==="
echo "This script will:"
echo "1. Deploy the infrastructure to AWS"
echo "2. Test the application"
echo "3. Destroy the infrastructure if tests pass"

# Process command line arguments
AUTO_DESTROY=true
for arg in "$@"; do
  case $arg in
    --no-destroy)
      AUTO_DESTROY=false
      shift
      ;;
    *)
      # Unknown option
      ;;
  esac
done

echo "Auto-destroy after testing: $AUTO_DESTROY"

echo ""
echo "=== Step 1: Deploying Infrastructure ==="
"${SCRIPT_DIR}/deploy.sh"
echo "=== Deployment Complete ==="
echo "Application endpoint: $(cd ${PROJECT_DIR}/terraform && terraform output -raw app_endpoint)"
echo "Run './scripts/test.sh' to test the application"

echo ""
echo "=== Step 2: Testing Application ==="
TEST_RESULT=0
"${SCRIPT_DIR}/test.sh" --non-interactive || TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
  echo ""
  echo "=== Tests Passed Successfully ==="

  if [ "$AUTO_DESTROY" = true ]; then
    echo ""
    echo "=== Step 3: Destroying Infrastructure ==="
    "${SCRIPT_DIR}/destroy.sh"
    echo "=== Cleanup Complete ==="
    echo "All AWS resources have been removed."
  else
    echo ""
    echo "Infrastructure will remain as requested with --no-destroy flag."
    echo "When you're ready to destroy it, run: ./scripts/destroy.sh"
  fi

  exit 0
else
  echo ""
  echo "=== Tests Failed ==="

  if [ "$AUTO_DESTROY" = true ]; then
    echo "Auto-destroying infrastructure despite test failures..."
    "${SCRIPT_DIR}/destroy.sh"
    echo "=== Cleanup Complete ==="
  else
    echo "Infrastructure will remain for debugging."
    echo "When you're ready to destroy it, run: ./scripts/destroy.sh"
  fi

  exit 1
fi
