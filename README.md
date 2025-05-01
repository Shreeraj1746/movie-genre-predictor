# Movie Genre Predictor

A complete end-to-end machine learning project that predicts movie genres based on plot summaries, orchestrated with Metaflow.

<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->

## Project Overview

This project demonstrates a complete ML workflow using Metaflow for orchestration:

1. Data acquisition from publicly available movie datasets
2. Data preprocessing and feature engineering
3. Training a text classification model (TF-IDF + Logistic Regression)
4. Model evaluation and versioning
5. Deployment as a FastAPI service on AWS EC2

## Learning Objectives

This project is designed as a learning journey to understand:

- ML workflow orchestration with Metaflow
- CI/CD for machine learning projects
- Infrastructure as Code with Terraform
- Deployment of ML models using FastAPI
- Best practices for Python development (linting, testing, etc.)

## Current Status

As of the latest update, the project has:

- ✅ Complete project structure with all necessary components
- ✅ Pre-commit hooks configured with ruff, black, and commitizen
- ✅ CI/CD pipeline with GitHub Actions
- ✅ AWS deployment infrastructure using Terraform
- ✅ Docker integration tests
- ✅ Comprehensive testing framework
- ✅ Makefile with convenient targets for testing and deployment
- ✅ Enhanced health check system with basic and advanced monitoring
- ✅ Deployment scripts with two-stage health checks and diagnostics

See [status.md](status.md) for detailed progress and next steps.

## Project Structure

```
movie-genre-predictor/
├── .github/                      # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml                # Run linting and tests
│       └── deploy.yml            # Deploy to EC2
├── data/                         # Data files
│   └── README.md                 # Data description and sources
├── terraform/                    # Terraform configurations
│   ├── main.tf                   # Main Terraform configuration
│   ├── variables.tf              # Terraform variables
│   ├── modules/                  # Terraform modules
│   └── templates/                # Templates for configuration
├── notebooks/                    # Jupyter notebooks for exploration
├── src/                          # Source code
│   ├── data/                     # Data processing code
│   │   ├── __init__.py
│   │   ├── download.py           # Data download scripts
│   │   └── preprocess.py         # Data preprocessing
│   ├── features/                 # Feature engineering
│   │   ├── __init__.py
│   │   └── text_features.py      # Text feature extraction
│   ├── model/                    # Model training and evaluation
│   │   ├── __init__.py
│   │   ├── train.py              # Model training
│   │   └── evaluate.py           # Model evaluation
│   ├── flows/                    # Metaflow workflows
│   │   ├── __init__.py
│   │   └── genre_classifier.py   # Main Metaflow workflow
│   └── api/                      # FastAPI application
│       ├── __init__.py
│       ├── main.py               # FastAPI app
│       └── models.py             # Pydantic models
├── tests/                        # Test files
│   ├── __init__.py
│   ├── test_api.py               # Test API endpoints
│   ├── test_features.py          # Test feature engineering
│   ├── test_model.py             # Test model training
│   └── test_integration.py       # End-to-end integration tests
├── scripts/                      # Deployment and utility scripts
├── models/                       # Saved model files
├── reports/                      # Generated analysis reports
├── .gitignore                    # Git ignore file
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker image definition
├── pyproject.toml                # Python project configuration
├── requirements.txt              # Project dependencies
├── requirements-dev.txt          # Development dependencies
├── run_integration_test.py       # Script to run Docker integration tests
├── setup.py                      # Package installation
├── Makefile                      # Automation commands
├── status.md                     # Project status tracker
└── README.md                     # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- Docker and Docker Compose (for integration testing)
- AWS account (for deployment)
- Terraform (for infrastructure)

### Local Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/movie-genre-predictor.git
   cd movie-genre-predictor
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Install pre-commit hooks:

   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

### Running the Project

The project includes a Makefile with convenient targets for common operations:

```bash
# Run all tests and linting
make all

# Run only unit tests
make test

# Run linting checks
make lint

# Run the integration test
make integration-test

```

For more detailed operations, see the specific commands below:

#### Data Download and Preprocessing

```bash
python -m src.data.download
python -m src.data.preprocess
```

#### Running the Metaflow Pipeline

```bash
python -m src.flows.genre_classifier run
```

#### Starting the API Locally

```bash
uvicorn src.api.main:app --reload
```

Visit <http://localhost:8000/docs> to see the API documentation.

## Docker Integration Testing

The project includes Docker-based integration testing for running the entire workflow in a containerized environment.

### Running Integration Tests

To run the integration tests:

```bash
# Run both integration test and workflow
python run_integration_test.py

# Run only the integration test
python run_integration_test.py --mode test

# Run only the workflow
python run_integration_test.py --mode workflow

# Build/use existing image and push to Docker Hub
python run_integration_test.py --push
```

See [docs/DOCKER.md](docs/DOCKER.md) for detailed Docker usage instructions.

## AWS Deployment with Terraform

This project includes automated infrastructure setup for deploying to AWS using Terraform.

### Running the Deployment Pipeline

To deploy, test, and (optionally) destroy the infrastructure:

```bash
./scripts/deploy_test_destroy.sh

# Keep infrastructure running after testing
./scripts/deploy_test_destroy.sh --no-destroy
```

### Deployment Architecture

The AWS infrastructure consists of:

- VPC with public subnets
- Security group with ports 22 (SSH), 8000 (API), and 8080 (health check)
- EC2 instance running the API
- S3 bucket for model storage
- IAM role for S3 access

### Deployment Features

- **Two-stage Health Checks**: Basic health endpoint (port 8080) and main API health check (port 8000)
- **Improved Resilience**: Validates deployment even if the main API is not fully operational
- **Graceful Degradation**: Simple HTTP server provides fallback functionality
- **Real-time Diagnostics**: Detailed health check responses for troubleshooting
- **Automatic Cleanup**: Resources are automatically destroyed after testing (if specified)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
