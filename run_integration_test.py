#!/usr/bin/env python3
"""
Run integration tests for the movie genre predictor project in Docker.

This script builds and runs a Docker container to execute the complete
end-to-end workflow and verify that all outputs are as expected.
"""

import argparse
import logging
import os
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_command(cmd, capture_output=True, check=False):
    """
    Run a shell command and handle its output.

    Args:
        cmd: Command to run (list of strings)
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise an exception on failure

    Returns:
        CompletedProcess instance
    """
    logger.info(f"Running command: {' '.join(cmd)}")

    if capture_output:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        return result
    else:
        return subprocess.run(cmd, check=check)


def build_docker_image():
    """Build the Docker image."""
    logger.info("Building Docker image...")

    cmd = ["docker", "build", "-t", "movie-genre-predictor:latest", "."]
    result = run_command(cmd)

    if result.returncode != 0:
        logger.error("Docker build failed!")
        sys.exit(1)

    logger.info("Docker image built successfully")


def run_integration_test_in_docker():
    """Run the integration test script in Docker."""
    logger.info("Running integration test in Docker...")

    # Ensure necessary directories exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    # Run the Docker container with the integration test
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{os.path.abspath('data')}:/app/data",
        "-v",
        f"{os.path.abspath('models')}:/app/models",
        "movie-genre-predictor:latest",
        "python",
        "-m",
        "tests.test_integration",
    ]

    result = run_command(cmd, capture_output=False)

    if result.returncode != 0:
        logger.error("Integration test failed!")
        sys.exit(1)

    logger.info("Integration test completed successfully!")


def run_full_workflow_in_docker():
    """Run the full workflow in Docker using docker-compose."""
    logger.info("Running full workflow in Docker using docker-compose...")

    # Ensure necessary directories exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    # Run docker-compose
    cmd = ["docker-compose", "up", "--build"]
    result = run_command(cmd, capture_output=False)

    if result.returncode != 0:
        logger.error("Docker-compose run failed!")
        sys.exit(1)

    logger.info("Full workflow completed successfully!")


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Run integration tests for the movie genre predictor project"
    )
    parser.add_argument(
        "--mode",
        choices=["test", "workflow", "all"],
        default="all",
        help=(
            "'test' for integration test only, 'workflow' for full workflow, "
            "or 'all' for both"
        ),
    )

    args = parser.parse_args()

    # Build Docker image
    build_docker_image()

    # Run selected mode
    if args.mode in ["test", "all"]:
        run_integration_test_in_docker()

    if args.mode in ["workflow", "all"]:
        run_full_workflow_in_docker()

    logger.info("All tests completed successfully!")


if __name__ == "__main__":
    main()
