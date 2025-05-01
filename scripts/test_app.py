#!/usr/bin/env python3
"""
Test script for the deployed movie genre predictor API.

This script tests the API endpoints of the deployed application
and validates the responses.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_app_endpoint() -> str:
    """
    Get the application endpoint from Terraform output.

    Returns:
        str: The application endpoint URL
    """
    # Get the terraform directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    terraform_dir = os.path.join(project_dir, "terraform")

    # Run terraform output command
    try:
        result = subprocess.run(
            ["terraform", "output", "-raw", "app_endpoint"],
            cwd=terraform_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        app_endpoint = result.stdout.strip()
        logger.info(f"Application endpoint: {app_endpoint}")
        return app_endpoint
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get application endpoint: {e}")
        logger.error(f"Stderr: {e.stderr}")
        sys.exit(1)


def wait_for_api_ready(
    endpoint: str, max_retries: int = 30, retry_interval: int = 10
) -> bool:
    """
    Wait for the API to be ready by checking the health endpoint.

    Args:
        endpoint: Base URL of the API
        max_retries: Maximum number of retries
        retry_interval: Interval between retries in seconds

    Returns:
        bool: True if the API is ready, False otherwise
    """
    health_url = f"{endpoint}/health"
    logger.info(f"Checking health at: {health_url}")

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} of {max_retries}...")
            response = requests.get(health_url, timeout=10)

            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "ok":
                    logger.info("API is ready!")
                    return True
                else:
                    logger.warning(
                        f"API health check returned status: {health_data.get('status')}"
                    )
            else:
                logger.warning(
                    f"Health check failed with status code: {response.status_code}"
                )

        except requests.RequestException as e:
            logger.warning(f"Request failed: {e}")

        if attempt < max_retries - 1:
            logger.info(f"Waiting {retry_interval} seconds before next attempt...")
            time.sleep(retry_interval)

    logger.error("API failed to become ready within the expected time")
    return False


def test_prediction(endpoint: str, plot: str) -> dict | None:
    """
    Test the prediction endpoint with a sample plot.

    Args:
        endpoint: Base URL of the API
        plot: Movie plot to predict genre for

    Returns:
        Optional[Dict]: Prediction results or None if failed
    """
    prediction_url = f"{endpoint}/predict"
    logger.info(f"Testing prediction at: {prediction_url}")

    payload = {"plot": plot}

    try:
        response = requests.post(
            prediction_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            logger.info("Prediction successful!")
            logger.info(f"Prediction: {json.dumps(result, indent=2)}")
            return result
        else:
            logger.error(f"Prediction failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Test the Movie Genre Predictor API")
    parser.add_argument(
        "--endpoint",
        help="API endpoint URL (optional, will use Terraform output if not provided)",
    )
    parser.add_argument(
        "--plot",
        help="Sample plot to test (optional, will use default if not provided)",
    )
    args = parser.parse_args()

    # Get the endpoint URL
    endpoint = args.endpoint if args.endpoint else get_app_endpoint()

    # Define a default sample plot if not provided
    default_plot = (
        "A young hacker joins a group of rebels fighting against an evil "
        "corporation that controls the virtual reality world everyone lives in."
    )
    plot = args.plot if args.plot else default_plot

    # Wait for the API to be ready
    if not wait_for_api_ready(endpoint):
        logger.error("Aborting test as API is not ready")
        sys.exit(1)

    # Test the prediction endpoint
    result = test_prediction(endpoint, plot)

    if result and "predictions" in result:
        logger.info("=== Test Successful ===")
        sys.exit(0)
    else:
        logger.error("=== Test Failed ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
