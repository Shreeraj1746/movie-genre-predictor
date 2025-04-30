#!/usr/bin/env python3
"""
Integration test for the movie genre predictor project.

This test script runs the entire workflow end-to-end and verifies
that all steps complete successfully with the expected outputs.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Directory paths
ROOT_DIR = Path(__file__).resolve().parents[1]  # project root directory
DATA_DIR = ROOT_DIR / "data"
SAMPLE_DATA_SCRIPT = DATA_DIR / "sample_data_generator.py"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT_DIR / "models"

# Expected minimum metrics (these should be realistic based on the sample data)
MIN_EXPECTED_ACCURACY = 0.5
MIN_EXPECTED_F1 = 0.5


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """
    Run a shell command and return the exit code, stdout, and stderr.

    Args:
        cmd: Command to run as a list of strings
        cwd: Working directory to run the command in (optional)

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    logger.info(f"Running command: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd if cwd else None,
    )

    stdout, stderr = process.communicate()
    exit_code = process.returncode

    return exit_code, stdout, stderr


def check_data_directories() -> bool:
    """
    Check if data directories exist and contain the required files.

    Returns:
        True if all directories and files exist, False otherwise
    """
    # Check raw data directory
    raw_data_dir = DATA_DIR / "raw"
    if not raw_data_dir.exists():
        logger.error(f"Raw data directory not found: {raw_data_dir}")
        return False

    # Check for required raw data files
    raw_files = ["movie.metadata.tsv", "plot_summaries.txt"]
    for filename in raw_files:
        if not (raw_data_dir / filename).exists():
            logger.error(f"Raw data file not found: {raw_data_dir / filename}")
            return False

    # Check processed data directory
    if not PROCESSED_DATA_DIR.exists():
        logger.error(f"Processed data directory not found: {PROCESSED_DATA_DIR}")
        return False

    # Check for required processed data files
    processed_files = [
        "train.csv",
        "validation.csv",
        "test.csv",
        "movies_with_plots.csv",
    ]
    for filename in processed_files:
        if not (PROCESSED_DATA_DIR / filename).exists():
            logger.error(
                f"Processed data file not found: {PROCESSED_DATA_DIR / filename}"
            )
            return False

    logger.info("All data directories and files exist")
    return True


def check_model_outputs() -> bool:
    """
    Check if model outputs exist and contain the required files.

    Returns:
        True if all directories and files exist, False otherwise
    """
    # Check models directory
    if not MODELS_DIR.exists():
        logger.error(f"Models directory not found: {MODELS_DIR}")
        return False

    # Find the most recent model directory (should be named with timestamp)
    model_dirs = list(MODELS_DIR.glob("logreg_*"))
    if not model_dirs:
        logger.error(f"No model directories found in {MODELS_DIR}")
        return False

    # Sort by creation time
    model_dir = sorted(model_dirs, key=lambda x: x.stat().st_ctime, reverse=True)[0]
    logger.info(f"Found model directory: {model_dir}")

    # Check for required model files
    model_files = [
        "genre_classifier.joblib",
        "feature_extractor.joblib",
        "model_info.json",
    ]
    for filename in model_files:
        if not (model_dir / filename).exists():
            logger.error(f"Model file not found: {model_dir / filename}")
            return False

    # Check model metrics
    with open(model_dir / "model_info.json") as f:
        model_info = json.load(f)

    # Print model metrics
    test_metrics = model_info.get("test_metrics", {})
    logger.info(f"Model test accuracy: {test_metrics.get('accuracy', 0):.4f}")
    logger.info(f"Model test F1 score: {test_metrics.get('f1', 0):.4f}")

    # Check if metrics meet minimum requirements
    accuracy = test_metrics.get("accuracy", 0)
    f1 = test_metrics.get("f1", 0)

    if accuracy < MIN_EXPECTED_ACCURACY:
        logger.error(
            f"Model accuracy too low: {accuracy:.4f} < {MIN_EXPECTED_ACCURACY}"
        )
        return False

    if f1 < MIN_EXPECTED_F1:
        logger.error(f"Model F1 score too low: {f1:.4f} < {MIN_EXPECTED_F1}")
        return False

    logger.info("Model outputs and metrics are valid")
    return True


def test_generate_sample_data():
    """Test that sample data generation works properly."""
    # Ensure data directories exist
    os.makedirs(DATA_DIR / "raw", exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    # Run sample data generator
    exit_code, stdout, stderr = run_command([sys.executable, str(SAMPLE_DATA_SCRIPT)])

    # Check that the command succeeded
    assert exit_code == 0, f"Sample data generation failed:\n{stderr}"

    # Check that the raw data files were created
    assert (DATA_DIR / "raw" / "movie.metadata.tsv").exists()
    assert (DATA_DIR / "raw" / "plot_summaries.txt").exists()

    logger.info("Sample data generation test passed")


def test_data_preprocessing():
    """Test that data preprocessing works properly."""
    # Run data preprocessing
    exit_code, stdout, stderr = run_command(
        [sys.executable, "-m", "src.data.preprocess"]
    )

    # Check that the command succeeded
    assert exit_code == 0, f"Data preprocessing failed:\n{stderr}"

    # Check that processed data files were created
    assert (PROCESSED_DATA_DIR / "train.csv").exists()
    assert (PROCESSED_DATA_DIR / "validation.csv").exists()
    assert (PROCESSED_DATA_DIR / "test.csv").exists()
    assert (PROCESSED_DATA_DIR / "movies_with_plots.csv").exists()

    # Check the processed data files contain data
    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DATA_DIR / "validation.csv")
    test_df = pd.read_csv(PROCESSED_DATA_DIR / "test.csv")

    assert len(train_df) > 0, "Training data is empty"
    assert len(val_df) > 0, "Validation data is empty"
    assert len(test_df) > 0, "Test data is empty"

    # Check for required columns
    required_columns = ["movie_id", "title", "genre", "plot"]
    for column in required_columns:
        assert (
            column in train_df.columns
        ), f"Column '{column}' missing from training data"

    logger.info("Data preprocessing test passed")


@pytest.mark.skip(
    reason=(
        "This test is designed to run in Docker, "
        "running locally may fail due to environment differences"
    )
)
def test_metaflow_workflow():
    """Test that the Metaflow workflow runs successfully end-to-end."""
    # Run the Metaflow workflow
    exit_code, stdout, stderr = run_command(
        [sys.executable, "-m", "src.flows.genre_classifier", "run"]
    )

    # Check that the command succeeded
    assert exit_code == 0, f"Metaflow workflow failed:\n{stderr}"

    # Check model outputs
    assert check_model_outputs(), "Model output validation failed"

    logger.info("Metaflow workflow test passed")


@pytest.mark.skip(
    reason=(
        "This test is designed to run in Docker, "
        "running locally may fail due to environment differences"
    )
)
def test_end_to_end():
    """Run all tests in sequence to validate the entire workflow."""
    test_generate_sample_data()
    test_data_preprocessing()
    test_metaflow_workflow()

    logger.info("End-to-end integration test passed successfully")


if __name__ == "__main__":
    # Run all tests
    logger.info("Starting integration tests")

    try:
        test_end_to_end()
        logger.info("All integration tests passed!")
        sys.exit(0)
    except AssertionError as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)
