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
│   └── test_api.py               # Test API endpoints
├── .gitignore                    # Git ignore file
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── pyproject.toml                # Python project configuration
├── requirements.txt              # Project dependencies
├── requirements-dev.txt          # Development dependencies
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
