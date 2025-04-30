#!/usr/bin/env python3
"""
Script to generate sample movie data for integration testing.

This script creates a small synthetic dataset that mimics the structure
of the CMU Movie Summary Corpus, but with a much smaller size suitable
for testing and committing to the repository.
"""

import json
import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Directory paths
ROOT_DIR = Path(__file__).resolve().parent  # data directory
RAW_DATA_DIR = ROOT_DIR / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "processed"

# Sample data constants
NUM_SAMPLES = 100
GENRES = ["Action", "Comedy", "Drama", "Sci-Fi", "Horror"]
RELEASE_YEARS = range(1990, 2023)
RUNTIME_RANGE = (60, 180)


def generate_plot_summary(genre: str) -> str:
    """
    Generate a synthetic plot summary for a movie.

    Args:
        genre: The genre of the movie

    Returns:
        A synthetic plot summary
    """
    # Plot elements by genre
    genre_elements = {
        "Action": [
            "A retired agent",
            "An elite soldier",
            "A former cop",
            "is forced back into action",
            "must save the world",
            "fights against a terrorist organization",
            "explosive confrontation",
            "dangerous mission",
            "car chase",
        ],
        "Comedy": [
            "A struggling writer",
            "Two best friends",
            "An awkward teenager",
            "embarks on a hilarious journey",
            "finds themselves in a ridiculous situation",
            "learns valuable lessons through humor",
            "comical misunderstanding",
            "funny encounter",
            "witty dialogue",
        ],
        "Drama": [
            "A troubled family",
            "A dedicated teacher",
            "A struggling artist",
            "faces personal demons",
            "overcomes life challenges",
            "deals with loss and redemption",
            "emotional confrontation",
            "difficult decision",
            "personal growth",
        ],
        "Sci-Fi": [
            "In a distant future",
            "On an alien planet",
            "After a technological breakthrough",
            "discovers a new form of life",
            "battles against artificial intelligence",
            "explores the boundaries of human consciousness",
            "interstellar travel",
            "advanced technology",
            "alien species",
        ],
        "Horror": [
            "A group of friends",
            "A young couple",
            "An unsuspecting family",
            "encounters a supernatural entity",
            "is haunted by past secrets",
            "discovers a cursed object",
            "terrifying revelation",
            "mysterious disappearance",
            "sinister presence",
        ],
    }

    elements = genre_elements[genre]
    subject = np.random.choice(elements[0:3])
    action = np.random.choice(elements[3:6])
    detail1 = np.random.choice(elements[6:9])
    detail2 = np.random.choice(elements[6:9])

    plot = f"{subject} {action} when confronted with a {detail1}. "
    plot += f"The story reaches its climax during a {detail2} that changes everything."

    return plot


def generate_metadata(movie_ids: list[int]) -> pd.DataFrame:
    """
    Generate synthetic movie metadata.

    Args:
        movie_ids: List of movie IDs to use

    Returns:
        DataFrame with synthetic metadata
    """
    metadata_rows = []

    for movie_id in movie_ids:
        genre_idx = movie_id % len(GENRES)
        genre = GENRES[genre_idx]
        title = f"Sample {genre} Movie {movie_id}"
        year = np.random.choice(RELEASE_YEARS)
        runtime = np.random.randint(*RUNTIME_RANGE)

        # Create genre in the format expected by the preprocessing script
        # Format: {"genre_id": "genre_name"} where genre_id needs to start with /
        genre_dict = {f"/genre/{genre.lower()}": genre}

        metadata_rows.append(
            {
                "movie_id": str(movie_id),
                "movie_name": title,
                "movie_release_date": f"{year}-01-01",
                "movie_box_office": str(np.random.randint(1000000, 100000000)),
                "movie_runtime": runtime,
                "movie_languages": json.dumps({"en": "English"}),
                "movie_countries": json.dumps({"usa": "United States of America"}),
                "movie_genres": json.dumps(genre_dict),
            }
        )

    df = pd.DataFrame(metadata_rows)
    logger.info(f"Generated metadata for {len(df)} movies")
    return df


def generate_plot_summaries(movie_ids: list[int]) -> pd.DataFrame:
    """
    Generate synthetic plot summaries.

    Args:
        movie_ids: List of movie IDs to use

    Returns:
        DataFrame with movie_id and plot columns
    """
    plot_rows = []

    for movie_id in movie_ids:
        # Determine the genre based on the movie_id (must be deterministic)
        genre_idx = movie_id % len(GENRES)
        genre = GENRES[genre_idx]

        plot = generate_plot_summary(genre)
        plot_rows.append({"movie_id": str(movie_id), "plot": plot})

    df = pd.DataFrame(plot_rows)
    logger.info(f"Generated plot summaries for {len(df)} movies")
    return df


def generate_sample_data(num_samples: int = NUM_SAMPLES) -> None:
    """
    Generate sample data files for testing.

    Args:
        num_samples: Number of sample movies to generate
    """
    logger.info(f"Generating sample data with {num_samples} movies")

    # Create directories
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Generate random movie IDs
    movie_ids = list(range(1, num_samples + 1))

    # Generate metadata
    metadata_df = generate_metadata(movie_ids)
    metadata_df.to_csv(
        RAW_DATA_DIR / "movie.metadata.tsv", sep="\t", index=False, header=False
    )

    # Generate plot summaries
    plots_df = generate_plot_summaries(movie_ids)
    plots_df.to_csv(
        RAW_DATA_DIR / "plot_summaries.txt", sep="\t", index=False, header=False
    )

    logger.info(f"Sample data saved to {RAW_DATA_DIR}")


if __name__ == "__main__":
    generate_sample_data()
