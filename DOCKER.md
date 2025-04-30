# Docker Usage Guide

This document explains how to use Docker with the movie-genre-predictor project.

## Docker Image Management

The project now supports smarter Docker image handling for integration tests and workflow execution:

1. First, it checks for a local image with the tag `movie-genre-predictor:latest`
2. If not found locally, it tries to pull the image from Docker Hub
3. Only if neither option is available, it builds the image locally

Both `run_integration_test.py` and `docker-compose.yml` now follow this pattern to avoid unnecessary rebuilds.

## Using the Integration Test Script

The updated `run_integration_test.py` script has the following options:

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

Run integration tests only:
```
python run_integration_test.py --mode test
```

Run the full workflow only:
```
python run_integration_test.py --mode workflow
```

Run both (default):
```
python run_integration_test.py
```

Build or use existing image and push to Docker Hub:
```
python run_integration_test.py --push
```

## Docker Hub Setup

To push images to Docker Hub:

1. Make sure you're logged in to Docker Hub:
   ```
   docker login
   ```

2. Update the `DOCKER_HUB_REPO` variable in `run_integration_test.py` to your Docker Hub username.

3. Run the integration test with the `--push` flag:
   ```
   python run_integration_test.py --push
   ```

## CI/CD Integration

For CI/CD pipelines, you can now avoid rebuilding the image on every run by:

1. Setting up automated pushes to Docker Hub when the main branch is updated
2. Using the script's intelligent image selection in your test pipelines

This allows you to save build time during testing while always ensuring you're using the correct image.

## Forcing a Rebuild

If you need to force a rebuild:

1. For integration tests only:
   ```
   docker image rm movie-genre-predictor:latest
   python run_integration_test.py
   ```

2. For docker-compose workflow:
   ```
   docker-compose build --no-cache
   docker-compose up
   ```
