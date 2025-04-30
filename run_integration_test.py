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

# Docker image details
IMAGE_NAME = "movie-genre-predictor"
IMAGE_TAG = "latest"
DOCKER_HUB_REPO = "shreeraj1746"
FULL_IMAGE_NAME = f"{IMAGE_NAME}:{IMAGE_TAG}"
DOCKER_HUB_IMAGE = f"{DOCKER_HUB_REPO}/{FULL_IMAGE_NAME}"


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


def check_image_exists_locally():
    """
    Check if the Docker image exists locally.

    Returns:
        bool: True if the image exists locally, False otherwise.
    """
    cmd = ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}", FULL_IMAGE_NAME]
    result = run_command(cmd)

    return (
        FULL_IMAGE_NAME in result.stdout.strip().split("\n") if result.stdout else False
    )


def pull_image_from_docker_hub():
    """
    Pull the Docker image from Docker Hub.

    Returns:
        bool: True if successful, False if failed.
    """
    logger.info(f"Attempting to pull image from Docker Hub: {DOCKER_HUB_IMAGE}")
    cmd = ["docker", "pull", DOCKER_HUB_IMAGE]
    result = run_command(cmd)

    if result.returncode != 0:
        logger.warning("Failed to pull image from Docker Hub")
        return False

    # Tag the pulled image with the local name
    if DOCKER_HUB_IMAGE != FULL_IMAGE_NAME:
        tag_cmd = ["docker", "tag", DOCKER_HUB_IMAGE, FULL_IMAGE_NAME]
        tag_result = run_command(tag_cmd)
        if tag_result.returncode != 0:
            logger.warning(f"Failed to tag pulled image as {FULL_IMAGE_NAME}")
            return False

    return True


def build_docker_image():
    """Build the Docker image locally."""
    logger.info("Building Docker image locally...")

    cmd = ["docker", "build", "-t", FULL_IMAGE_NAME, "."]
    result = run_command(cmd)

    if result.returncode != 0:
        logger.error("Docker build failed!")
        sys.exit(1)

    logger.info("Docker image built successfully")
    return True


def ensure_docker_image():
    """
    Ensure the Docker image is available using the following order:
    1. Use local image if available
    2. Pull from Docker Hub if available
    3. Build locally if neither of the above is available

    Returns:
        bool: True if the image is available
    """
    # Check if image exists locally
    if check_image_exists_locally():
        logger.info(f"Using existing local Docker image: {FULL_IMAGE_NAME}")
        return True

    # Try to pull from Docker Hub
    if pull_image_from_docker_hub():
        logger.info(
            f"Successfully pulled Docker image from Docker Hub: {DOCKER_HUB_IMAGE}"
        )
        return True

    # Build locally as last resort
    logger.info("No existing image found locally or on Docker Hub. Building image...")
    return build_docker_image()


def push_to_docker_hub():
    """
    Push the built image to Docker Hub.

    Returns:
        bool: True if successful, False otherwise
    """
    # First tag the image with the Docker Hub repository name
    if DOCKER_HUB_IMAGE != FULL_IMAGE_NAME:
        tag_cmd = ["docker", "tag", FULL_IMAGE_NAME, DOCKER_HUB_IMAGE]
        tag_result = run_command(tag_cmd)
        if tag_result.returncode != 0:
            logger.error(f"Failed to tag image for Docker Hub: {DOCKER_HUB_IMAGE}")
            return False

    # Push to Docker Hub
    logger.info(f"Pushing image to Docker Hub: {DOCKER_HUB_IMAGE}")
    push_cmd = ["docker", "push", DOCKER_HUB_IMAGE]
    push_result = run_command(push_cmd)

    if push_result.returncode != 0:
        logger.error("Failed to push image to Docker Hub")
        return False

    logger.info(f"Successfully pushed image to Docker Hub: {DOCKER_HUB_IMAGE}")
    return True


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
        FULL_IMAGE_NAME,
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

    # Run docker-compose without the --build flag to use the existing image
    cmd = ["docker-compose", "up"]
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
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the Docker image to Docker Hub after building",
    )

    args = parser.parse_args()

    # Ensure Docker image is available
    ensure_docker_image()

    # Push to Docker Hub if requested
    if args.push:
        push_to_docker_hub()

    # Run selected mode
    if args.mode in ["test", "all"]:
        run_integration_test_in_docker()

    if args.mode in ["workflow", "all"]:
        run_full_workflow_in_docker()

    logger.info("All tests completed successfully!")


if __name__ == "__main__":
    main()
