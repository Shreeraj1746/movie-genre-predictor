.PHONY: clean test integration-test all lint install install-dev help venv

# Check Python version
PY_VERSION_FULL := $(shell python --version 2>&1)
PY_VERSION_MAJOR := $(shell echo $(PY_VERSION_FULL) | sed -r 's/Python ([0-9]+)\..*/\1/')
PY_VERSION_MINOR := $(shell echo $(PY_VERSION_FULL) | sed -r 's/Python [0-9]+\.([0-9]+).*/\1/')

# Python interpreter to use - default to python command
PYTHON := python

# Default target
all: install-dev lint test

# Help message
help:
	@echo "Available targets:"
	@echo "  help           - Show this help message"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  lint           - Run linting checks"
	@echo "  test           - Run unit tests"
	@echo "  integration-test - Run integration tests in Docker"
	@echo "  integration-test-only - Run only the integration test in Docker"
	@echo "  workflow-only  - Run only the full workflow in Docker"
	@echo "  clean          - Remove build artifacts and cache directories"
	@echo "  all            - Run lint and tests (default)"
	@echo "  venv           - Create a virtual environment"
	@echo
	@echo "Current Python version: $(PY_VERSION_FULL)"

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "Activate the virtual environment with: source venv/bin/activate"

# Install production dependencies
install: check-venv
	@echo "Installing dependencies from requirements.txt..."
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -r requirements.txt

# Install development dependencies
install-dev: install
	@echo "Installing development dependencies from requirements-dev.txt..."
	$(PYTHON) -m pip install -r requirements-dev.txt
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "Making Git hooks executable..."
	chmod +x .git/hooks/pre-commit .git/hooks/pre-push .git/hooks/commit-msg || true

# Run linting
lint: check-venv
	@echo "Running linting checks..."
	pre-commit run --all-files

# Run unit tests
test: check-venv
	@echo "Running unit tests..."
	$(PYTHON) -m pytest tests/ --verbose --cov=src --cov-report=term-missing

# Run integration tests in Docker
integration-test:
	@echo "Running full integration test in Docker..."
	$(PYTHON) run_integration_test.py

# Run only the integration test part in Docker
integration-test-only:
	@echo "Running integration test only in Docker..."
	$(PYTHON) run_integration_test.py --mode test

# Run only the workflow part in Docker
workflow-only:
	@echo "Running workflow only in Docker..."
	$(PYTHON) run_integration_test.py --mode workflow

# Clean up build artifacts and cache directories
clean:
	@echo "Cleaning up build artifacts and cache directories..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .coverage.*
	rm -rf htmlcov/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Helper to check if in a virtual environment
check-venv:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "WARNING: Not running in a virtual environment. It's recommended to run 'make venv' and activate it."; \
	fi
