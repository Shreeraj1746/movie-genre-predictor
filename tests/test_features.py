#!/usr/bin/env python3
"""
Tests for the text feature extraction module.
"""

import tempfile
from pathlib import Path

import numpy as np

from src.features.text_features import TextFeatureExtractor


def test_tfidf_extraction():
    """Test TF-IDF feature extraction."""
    # Create test data
    texts = [
        "This is a test document about movies",
        "Another test document about science fiction",
        "A third document about action movies and drama",
    ]

    # Create feature extractor
    extractor = TextFeatureExtractor(max_features=100)

    # Test fit_transform
    features = extractor.fit_transform_tfidf(texts)

    # Check that features have the expected shape
    assert features.shape[0] == len(texts)
    assert features.shape[1] <= 100

    # Check that we can transform new data
    new_text = ["A new document about comedy movies"]
    new_features = extractor.transform_tfidf(new_text)

    # Check that the new features have the expected shape
    assert new_features.shape[0] == len(new_text)
    assert new_features.shape[1] == features.shape[1]


def test_save_load():
    """Test saving and loading the feature extractor."""
    # Create test data
    texts = [
        "This is a test document about movies",
        "Another test document about science fiction",
        "A third document about action movies and drama",
    ]

    # Create and fit feature extractor
    extractor = TextFeatureExtractor(max_features=50)
    features = extractor.fit_transform_tfidf(texts)

    # Save to a temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "feature_extractor.pkl"
        extractor.save(save_path)

        # Load from the file
        loaded_extractor = TextFeatureExtractor.load(save_path)

        # Transform using the loaded extractor
        loaded_features = loaded_extractor.transform_tfidf(texts)

        # Check that the features are the same
        np.testing.assert_array_equal(features.toarray(), loaded_features.toarray())

        # Check that the attributes are preserved
        assert loaded_extractor.max_features == extractor.max_features
        assert loaded_extractor.ngram_range == extractor.ngram_range


def test_top_features():
    """Test get_top_features method."""
    # Create test data
    texts = [
        "This is a test document about movies and cinema",
        "Another test document about science fiction films",
        "A third document about action movies and drama shows",
        "Movies about space and science fiction",
        "Drama and comedy in cinema productions",
    ]

    # Create and fit feature extractor
    extractor = TextFeatureExtractor(max_features=20)
    extractor.fit_tfidf(texts)

    # Get top features
    top_features = extractor.get_top_features(5)

    # Check that we get the expected number of features
    assert len(top_features) == 5

    # Check that all top features are in the vocabulary
    for feature in top_features:
        assert feature in extractor.tfidf_vectorizer.vocabulary_
