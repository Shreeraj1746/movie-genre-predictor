#!/usr/bin/env python3
"""
Preprocessing script for the CMU Movie Summary Corpus.

This script loads the raw movie data, performs preprocessing steps, and
creates train/test/validation splits for the genre classification task.
"""

import json
import logging
import os
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Directory paths
ROOT_DIR = Path(__file__).resolve().parents[2]  # project root directory
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

# Minimum examples per genre (use smaller value for testing)
MIN_EXAMPLES_PER_GENRE = 5


def load_metadata(filepath: Path) -> pd.DataFrame:
    """
    Load and parse the movie metadata TSV file.

    Args:
        filepath: Path to the metadata TSV file

    Returns:
        DataFrame containing the parsed metadata
    """
    logger.info(f"Loading metadata from {filepath}")

    columns = [
        "movie_id",
        "movie_name",
        "movie_release_date",
        "movie_box_office",
        "movie_runtime",
        "movie_languages",
        "movie_countries",
        "movie_genres",
    ]

    df = pd.read_csv(filepath, sep="\t", header=None, names=columns)

    # Parse JSON fields
    for col in ["movie_genres", "movie_languages", "movie_countries"]:
        df[col] = df[col].apply(lambda x: json.loads(x) if pd.notna(x) else {})

    # Extract primary genre (first listed genre)
    df["primary_genre"] = df["movie_genres"].apply(
        lambda x: list(x.values())[0] if x and len(x) > 0 else "Unknown"
    )

    # Extract year from release date
    df["release_year"] = pd.to_numeric(
        df["movie_release_date"].str.extract(r"(\d{4})")[0], errors="coerce"
    )

    logger.info(f"Loaded metadata for {len(df)} movies")
    return df


def load_plot_summaries(filepath: Path) -> pd.DataFrame:
    """
    Load movie plot summaries.

    Args:
        filepath: Path to the plot summaries file

    Returns:
        DataFrame containing movie_id and plot text
    """
    logger.info(f"Loading plot summaries from {filepath}")

    df = pd.read_csv(filepath, sep="\t", header=None, names=["movie_id", "plot"])

    logger.info(f"Loaded {len(df)} plot summaries")
    return df


def clean_text(text: str) -> str:
    """
    Clean and normalize text data.

    Args:
        text: Input text to clean

    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""

    # Basic cleaning
    text = text.lower()
    text = text.replace("\n", " ").replace("\r", " ")

    # Could add more advanced cleaning here, like:
    # - Removing HTML tags
    # - Removing special characters
    # - Lemmatization
    # - Stopword removal

    return text


def merge_and_clean_data(
    metadata_df: pd.DataFrame, plots_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge metadata with plot summaries and clean the data.

    Args:
        metadata_df: DataFrame containing movie metadata
        plots_df: DataFrame containing plot summaries

    Returns:
        Merged and cleaned DataFrame
    """
    logger.info("Merging metadata with plot summaries")

    # Merge on movie_id
    merged_df = pd.merge(metadata_df, plots_df, on="movie_id", how="inner")

    logger.info(f"Merged data contains {len(merged_df)} movies")

    # Clean plot text
    merged_df["plot_clean"] = merged_df["plot"].apply(clean_text)

    # Drop rows with missing essential data
    merged_df = merged_df.dropna(subset=["plot_clean", "primary_genre"])

    # Keep only common genres (minimum examples)
    genre_counts = merged_df["primary_genre"].value_counts()
    common_genres = genre_counts[genre_counts >= MIN_EXAMPLES_PER_GENRE].index.tolist()
    merged_df = merged_df[merged_df["primary_genre"].isin(common_genres)]

    # Select final columns for the processed dataset
    final_df = merged_df[
        [
            "movie_id",
            "movie_name",
            "primary_genre",
            "plot_clean",
            "release_year",
            "movie_runtime",
        ]
    ].rename(
        columns={
            "movie_name": "title",
            "primary_genre": "genre",
            "plot_clean": "plot",
            "movie_runtime": "runtime",
        }
    )

    logger.info(f"Final cleaned dataset contains {len(final_df)} movies")
    logger.info(f"Genre distribution:\n{final_df['genre'].value_counts()}")

    return final_df


def create_data_splits(
    df: pd.DataFrame,
    test_size: float = 0.2,
    val_size: float = 0.1,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split data into train, validation, and test sets.

    Args:
        df: Input DataFrame
        test_size: Fraction of data to use for testing
        val_size: Fraction of data to use for validation
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    logger.info("Creating train/validation/test splits")

    # First split: training + validation vs test
    train_val_df, test_df = train_test_split(
        df, test_size=test_size, random_state=random_state, stratify=df["genre"]
    )

    # Second split: training vs validation
    # Adjust validation size to account for the first split
    adjusted_val_size = val_size / (1 - test_size)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=adjusted_val_size,
        random_state=random_state,
        stratify=train_val_df["genre"],
    )

    logger.info(
        f"Created splits: train={len(train_df)}, "
        f"validation={len(val_df)}, test={len(test_df)}"
    )

    return train_df, val_df, test_df


def save_processed_data(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    full_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    """
    Save processed datasets to CSV files.

    Args:
        train_df: Training DataFrame
        val_df: Validation DataFrame
        test_df: Test DataFrame
        full_df: Complete processed DataFrame
        output_dir: Directory to save the files to
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save split datasets
    train_df.to_csv(output_dir / "train.csv", index=False)
    val_df.to_csv(output_dir / "validation.csv", index=False)
    test_df.to_csv(output_dir / "test.csv", index=False)

    # Save full dataset
    full_df.to_csv(output_dir / "movies_with_plots.csv", index=False)

    # Save genre label mapping
    genre_labels = dict(enumerate(sorted(full_df["genre"].unique())))
    pd.DataFrame(
        {"index": list(genre_labels.keys()), "genre": list(genre_labels.values())}
    ).to_csv(output_dir / "genre_labels.csv", index=False)

    logger.info(f"Saved processed datasets to {output_dir}")


def preprocess_data(output_dir: Path | None = None) -> bool:
    """
    Main preprocessing function to handle the movie dataset.

    Args:
        output_dir: Directory to save processed data.
            Defaults to data/processed in the project root

    Returns:
        bool: True if processing succeeded, False otherwise
    """
    if output_dir is None:
        output_dir = PROCESSED_DATA_DIR

    try:
        # Load raw data
        metadata_filepath = RAW_DATA_DIR / "movie.metadata.tsv"
        plots_filepath = RAW_DATA_DIR / "plot_summaries.txt"

        if not metadata_filepath.exists() or not plots_filepath.exists():
            logger.error("Raw data files not found. Run download.py first.")
            return False

        metadata_df = load_metadata(metadata_filepath)
        plots_df = load_plot_summaries(plots_filepath)

        # Merge and clean data
        processed_df = merge_and_clean_data(metadata_df, plots_df)

        # Create train/test/validation splits
        train_df, val_df, test_df = create_data_splits(processed_df)

        # Save processed data
        save_processed_data(train_df, val_df, test_df, processed_df, output_dir)

        return True
    except Exception as e:
        logger.error(f"Error preprocessing data: {e}")
        return False


if __name__ == "__main__":
    preprocess_data()
