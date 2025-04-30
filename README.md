# Movie Genre Predictor

A complete end-to-end machine learning project that predicts movie genres based on plot summaries, orchestrated with Metaflow.

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

## Project Structure

```
movie-genre-predictor/
├── .github/                      # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml                # Run linting and tests
│       └── deploy.yml            # Deploy to EC2
├── data/                         # Data files
│   └── README.md                 # Data description and sources
├── infrastructure/               # Terraform configurations
│   ├── main.tf                   # Main Terraform configuration
│   ├── variables.tf              # Terraform variables
│   └── outputs.tf                # Terraform outputs
├── notebooks/                    # Jupyter notebooks for exploration
│   └── data_exploration.ipynb    # Initial data exploration
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
│   ├── test_data.py              # Test data processing
│   ├── test_features.py          # Test feature engineering
│   ├── test_model.py             # Test model training
│   ├── test_api.py               # Test API endpoints
│   └── test_integration.py       # End-to-end integration tests
├── .gitignore                    # Git ignore file
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker image definition
├── pyproject.toml                # Python project configuration
├── requirements.txt              # Project dependencies
├── requirements-dev.txt          # Development dependencies
├── run_integration_test.py       # Script to run Docker integration tests
├── setup.py                      # Package installation
├── status.md                     # Project status tracker
└── README.md                     # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.10+
- Git
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
   source venv/bin/activate
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

## Running Tests Locally

### Unit Tests

The project includes a comprehensive test suite to ensure code quality and reliability. You can run the unit tests using the Make target:

```bash
make test
```

This command will execute all unit tests and provide coverage information, showing which parts of the codebase are tested and which are not.

To run specific tests, you can use pytest directly:

```bash
python -m pytest tests/test_model.py
```

### Running All Quality Checks

To run both linting and tests in one command:

```bash
make all
```

## Docker Integration Testing

The project includes a Docker-based integration testing setup for running the entire workflow locally in a containerized environment.

### Prerequisites

- Docker
- Docker Compose

### Running Integration Tests

To run the full integration test suite:

```bash
make integration-test
```

This command:
1. Builds a Docker image with the entire project
2. Runs the integration test inside a Docker container
3. Executes the end-to-end workflow using Docker Compose

You can also run specific parts of the test:

```bash
# Run only the integration test
make integration-test-only

# Run only the full workflow
make workflow-only
```

### Test Dataset

For integration testing, the project includes a sample data generator that creates a small synthetic dataset that mimics the structure of the full CMU Movie Summary Corpus. The sample data is small enough to be checked into the repository and serves as the "gold" test dataset.

To generate the sample data manually:

```bash
python data/sample_data_generator.py
```

### Workflow Outputs

After running the integration test, the following outputs will be generated:

- Preprocessed data files in `data/processed/`
- Trained model files in `models/logreg_*` (with timestamp)
- Evaluation metrics in `models/logreg_*/model_info.json`

These outputs are checked against expected values to ensure the workflow functions correctly.

## CI/CD Pipeline

This project uses GitHub Actions for CI/CD:

### Continuous Integration (CI)

The CI workflow (`ci.yml`) runs on every push and pull request:

- Runs pre-commit hooks (ruff, black, commitizen)
- Executes unit tests
- Builds project artifacts

### Continuous Deployment (CD)

The CD workflow (`deploy.yml`) runs when changes are pushed to the main branch:

- Connects to the EC2 instance via SSH
- Pulls the latest code
- Installs dependencies
- Restarts the FastAPI service

## AWS Deployment

The project is deployed to AWS EC2 (t3.micro instance) using Terraform:

1. Configure AWS credentials:

   ```bash
   aws configure
   ```

2. Initialize and apply Terraform:

   ```bash
   cd infrastructure
   terraform init
   terraform apply
   ```

3. The FastAPI application will be automatically deployed by the CD pipeline.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
