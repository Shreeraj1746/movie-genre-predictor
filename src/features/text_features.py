#!/usr/bin/env python3
"""
Text feature extraction module for movie plot summaries.

This module provides functions to extract text features from movie plot
summaries using various techniques like TF-IDF and text preprocessing.
"""

import logging
import pickle
from pathlib import Path
from typing import Union, Optional, List, Dict, Any

import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Download required NLTK resources
def download_nltk_resources() -> None:
    """Download required NLTK resources if not already present."""
    try:
        resources = ["punkt", "stopwords", "wordnet"]
        for resource in resources:
            try:
                nltk.data.find(f"tokenizers/{resource}")
            except LookupError:
                nltk.download(resource, quiet=True)
        logger.info("NLTK resources downloaded")
    except Exception as e:
        logger.warning(f"Error downloading NLTK resources: {e}")


class TextFeatureExtractor:
    """
    Class for extracting features from text data.

    This class provides methods to extract TF-IDF features from movie plot
    summaries and other text preprocessing utilities.
    """

    def __init__(
        self,
        max_features: int = 10000,
        ngram_range: tuple = (1, 2),
        min_df: Union[float, int] = 2,
        max_df: Union[float, int] = 0.95,
        stop_words: str = "english",
    ):
        """
        Initialize the TextFeatureExtractor.

        Args:
            max_features: Maximum number of features to extract
            ngram_range: Range of n-grams to consider (e.g., (1, 2) for unigrams and bigrams)
            min_df: Minimum document frequency for terms
            max_df: Maximum document frequency for terms
            stop_words: Stop words to exclude (e.g., "english" or a list of words)
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.stop_words = stop_words

        # Initialize vectorizers
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            stop_words=stop_words,
        )

        self.count_vectorizer = CountVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            stop_words=stop_words,
        )

        # Download NLTK resources if needed
        download_nltk_resources()

    def fit_tfidf(self, texts: List[str]) -> "TextFeatureExtractor":
        """
        Fit the TF-IDF vectorizer on a corpus of texts.

        Args:
            texts: List of text documents to fit on

        Returns:
            Self for method chaining
        """
        logger.info("Fitting TF-IDF vectorizer on text corpus")
        self.tfidf_vectorizer.fit(texts)
        logger.info(f"TF-IDF vocabulary size: {len(self.tfidf_vectorizer.vocabulary_)}")
        return self

    def transform_tfidf(self, texts: List[str]) -> np.ndarray:
        """
        Transform texts into TF-IDF feature vectors.

        Args:
            texts: List of text documents to transform

        Returns:
            Array of TF-IDF feature vectors
        """
        logger.info(f"Transforming {len(texts)} texts to TF-IDF features")
        return self.tfidf_vectorizer.transform(texts)

    def fit_transform_tfidf(self, texts: List[str]) -> np.ndarray:
        """
        Fit the TF-IDF vectorizer and transform texts in one step.

        Args:
            texts: List of text documents to fit and transform

        Returns:
            Array of TF-IDF feature vectors
        """
        logger.info(f"Fit-transforming {len(texts)} texts to TF-IDF features")
        return self.tfidf_vectorizer.fit_transform(texts)

    def get_top_features(self, n: int = 20) -> List[str]:
        """
        Get the top n features (terms) from the TF-IDF vectorizer.

        Args:
            n: Number of top features to return

        Returns:
            List of top feature terms
        """
        if not hasattr(self.tfidf_vectorizer, "vocabulary_"):
            logger.warning("TF-IDF vectorizer not yet fitted")
            return []

        vocab = self.tfidf_vectorizer.vocabulary_
        idx_to_term = {idx: term for term, idx in vocab.items()}
        top_idxs = sorted(vocab.values(), key=lambda idx: -idx)[:n]
        return [idx_to_term[idx] for idx in top_idxs]

    def save(self, filepath: Path) -> None:
        """
        Save the feature extractor to a file.

        Args:
            filepath: Path to save the feature extractor to
        """
        logger.info(f"Saving TextFeatureExtractor to {filepath}")
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath: Path) -> "TextFeatureExtractor":
        """
        Load a feature extractor from a file.

        Args:
            filepath: Path to load the feature extractor from

        Returns:
            Loaded TextFeatureExtractor instance
        """
        logger.info(f"Loading TextFeatureExtractor from {filepath}")
        with open(filepath, "rb") as f:
            return pickle.load(f)


if __name__ == "__main__":
    # Example usage
    example_texts = [
        "A thrilling adventure in the mountains with dangerous wildlife.",
        "A romantic comedy about two people who meet in the city.",
        "An action-packed sci-fi movie with aliens and spaceships.",
    ]

    extractor = TextFeatureExtractor(max_features=100)
    features = extractor.fit_transform_tfidf(example_texts)

    print(f"Feature matrix shape: {features.shape}")
    print(f"Top features: {extractor.get_top_features(10)}")
