#!/usr/bin/env python3
"""
Script to download the CMU Movie Summary Corpus.

This script downloads plot summaries and movie metadata from the
CMU Movie Summary Corpus and saves them to the data/raw directory.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional

import requests
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# URLs for the dataset files
DATASET_URLS: Dict[str, str] = {
    "plot_summaries.txt": "http://www.cs.cmu.edu/~ark/personas/data/plot_summaries.txt",
    "movie.metadata.tsv": "http://www.cs.cmu.edu/~ark/personas/data/movie.metadata.tsv",
}

# Directory paths
ROOT_DIR = Path(__file__).resolve().parents[2]  # project root directory
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"


def download_file(url: str, filepath: Path, chunk_size: int = 8192) -> None:
    """
    Download a file from a URL to a specified path.

    Args:
        url: URL to download the file from
        filepath: Path to save the file to
        chunk_size: Size of chunks to download at a time (in bytes)

    Raises:
        requests.exceptions.RequestException: If the download fails
    """
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        progress_bar = tqdm(
            total=total_size, unit="B", unit_scale=True, desc=filepath.name
        )

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        progress_bar.close()

        logger.info(f"Downloaded {filepath.name} successfully")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading {url}: {e}")
        raise


def download_dataset(output_dir: Optional[Path] = None) -> bool:
    """
    Download the CMU Movie Summary Corpus dataset.

    Args:
        output_dir: Directory to save the dataset files to.
            Defaults to data/raw in the project root

    Returns:
        bool: True if all downloads succeeded, False otherwise
    """
    if output_dir is None:
        output_dir = RAW_DATA_DIR

    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Downloading dataset to {output_dir}")

    success = True
    for filename, url in DATASET_URLS.items():
        filepath = output_dir / filename
        if filepath.exists():
            logger.info(f"File {filename} already exists, skipping download")
            continue

        try:
            download_file(url, filepath)
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            success = False

    if success:
        logger.info("Dataset download completed successfully")
    else:
        logger.warning("Some files failed to download")

    return success


if __name__ == "__main__":
    download_dataset()
