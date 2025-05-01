# Docker Usage Guide

This document explains how to use Docker with the movie-genre-predictor project.

## Docker Image Management

The project uses an intelligent Docker image handling system that minimizes unnecessary rebuilds:

1. First, it checks for a local image with the tag `movie-genre-predictor:latest`
2. If not found locally, it tries to pull the image from Docker Hub
3. Only if neither option is available, it builds the image locally

Both `run_integration_test.py` and `docker-compose.yml` follow this pattern to optimize build time.

## Integration Testing with Docker

### Using the Integration Test Script

The `run_integration_test.py` script provides a flexible way to run integration tests:

```
usage: run_integration_test.py [-h] [--mode {test,workflow,all}] [--push]

Run integration tests for the movie genre predictor project

options:
  -h, --help            show this help message and exit
  --mode {test,workflow,all}
                        'test' for integration test only, 'workflow' for full
                        workflow, or 'all' for both
  --push                Push the Docker image to Docker Hub after building
```

### Examples

```bash
# Run both integration test and workflow (default)
python run_integration_test.py

# Run integration tests only
python run_integration_test.py --mode test

# Run the full workflow only
python run_integration_test.py --mode workflow

# Build or use existing image and push to Docker Hub
python run_integration_test.py --push
```

### Using Make Targets

The project's Makefile also provides convenient targets for Docker operations:

```bash
# Run the full integration test suite
make integration-test

# Run only the integration test
make integration-test-only

# Run only the workflow
make workflow-only
```

## Docker Hub Integration

To push images to Docker Hub:

1. Make sure you're logged in to Docker Hub:
   ```bash
   docker login
   ```

2. Update the `DOCKER_HUB_REPO` variable in `run_integration_test.py` to your Docker Hub username.

3. Run the integration test with the `--push` flag:
   ```bash
   python run_integration_test.py --push
   ```

## CI/CD Integration

The project is configured for CI/CD pipelines with Docker:

1. The CI workflow uses Docker Hub images when available to save build time
2. Image builds occur only when necessary based on code changes
3. Integration tests run against the Docker images to ensure consistent behavior

## Managing Docker Images

### Forcing a Rebuild

If you need to force a rebuild:

1. Remove the existing image:
   ```bash
   docker image rm movie-genre-predictor:latest
   ```

2. Run the integration test or workflow:
   ```bash
   python run_integration_test.py
   ```

3. For docker-compose workflow:
   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

### Cleaning Up Docker Resources

To clean up unused Docker resources:

```bash
# Remove unused images
docker image prune -a

# Remove unused containers
docker container prune

# Remove all unused Docker resources
docker system prune
```
