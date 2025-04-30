FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
COPY requirements-dev.txt .
COPY setup.py .
COPY pyproject.toml .
COPY src/ ./src/
COPY tests/ ./tests/
COPY data/ ./data/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
RUN pip install -e .

# Make directories that might be needed
RUN mkdir -p data/raw data/processed models/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV USERNAME=docker-user
ENV METAFLOW_DEFAULT_DATASTORE=local
ENV METAFLOW_DEFAULT_METADATA=local
ENV METAFLOW_USER=docker-user

# Default command
CMD ["bash"]
