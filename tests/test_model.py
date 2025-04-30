#!/usr/bin/env python3
"""
Tests for the model training module.
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from sklearn.datasets import make_classification

from src.model.train import GenreClassifier, train_model


def test_genre_classifier_initialization():
    """Test initialization of the GenreClassifier class."""
    classifier = GenreClassifier(model_type="logreg")
    assert classifier.model_type == "logreg"
    assert classifier.model is None

    classifier = GenreClassifier(model_type="naive_bayes", model_params={"alpha": 0.5})
    assert classifier.model_type == "naive_bayes"
    assert classifier.model_params == {"alpha": 0.5}


def test_genre_classifier_training():
    """Test training of the GenreClassifier."""
    # Create synthetic data
    features, y_encoded = make_classification(
        n_samples=100, n_features=20, n_classes=3, n_informative=4, random_state=42
    )

    # Convert encoded labels to genre strings
    genres = ["action", "comedy", "drama"]
    y = np.array(genres)[y_encoded]

    # Create and train classifier
    classifier = GenreClassifier(model_type="logreg")
    classifier.fit(features, y)

    # Check that the model was created
    assert classifier.model is not None

    # Check that the label encoder was fitted
    assert len(classifier.label_encoder.classes_) == len(genres)
    assert set(classifier.label_encoder.classes_) == set(genres)

    # Test prediction
    y_pred = classifier.predict(features[:5])
    assert len(y_pred) == 5
    assert all(genre in genres for genre in y_pred)


def test_genre_classifier_save_load():
    """Test saving and loading of the GenreClassifier."""
    # Create synthetic data
    features, y_encoded = make_classification(
        n_samples=100, n_features=20, n_classes=3, n_informative=4, random_state=42
    )

    # Convert encoded labels to genre strings
    genres = ["action", "comedy", "drama"]
    y = np.array(genres)[y_encoded]

    # Create and train classifier
    classifier = GenreClassifier(model_type="logreg")
    classifier.fit(features, y)

    # Save to a temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "model.joblib"
        classifier.save(save_path)

        # Load from the file
        loaded_classifier = GenreClassifier.load(save_path)

        # Check that attributes were preserved
        assert loaded_classifier.model_type == classifier.model_type
        assert loaded_classifier.model is not None

        # Check that predictions are the same
        y_pred_original = classifier.predict(features[:5])
        y_pred_loaded = loaded_classifier.predict(features[:5])
        np.testing.assert_array_equal(y_pred_original, y_pred_loaded)


def test_train_model_function():
    """Test the train_model helper function."""
    # Create synthetic data
    features, y_encoded = make_classification(
        n_samples=100, n_features=20, n_classes=3, n_informative=4, random_state=42
    )

    # Convert encoded labels to genre strings
    genres = ["action", "comedy", "drama"]
    y = np.array(genres)[y_encoded]

    # Train model using the helper function
    model = train_model(features, y, model_type="logreg")

    # Check that the model was created and trained
    assert model.model is not None
    assert model.model_type == "logreg"

    # Test prediction
    y_pred = model.predict(features[:5])
    assert len(y_pred) == 5
    assert all(genre in genres for genre in y_pred)


def test_different_model_types():
    """Test different model types."""
    # Create synthetic data
    features, y_encoded = make_classification(
        n_samples=100, n_features=20, n_classes=3, n_informative=4, random_state=42
    )

    # Make all features non-negative for Naive Bayes
    features = np.abs(features)

    # Convert encoded labels to genre strings
    genres = ["action", "comedy", "drama"]
    y = np.array(genres)[y_encoded]

    # Test logistic regression
    logreg_model = train_model(features, y, model_type="logreg")
    assert logreg_model.model_type == "logreg"
    assert logreg_model.predict(features[:1])[0] in genres

    # Test naive Bayes
    nb_model = train_model(features, y, model_type="naive_bayes")
    assert nb_model.model_type == "naive_bayes"
    assert nb_model.predict(features[:1])[0] in genres

    # Test random forest
    rf_model = train_model(features, y, model_type="random_forest")
    assert rf_model.model_type == "random_forest"
    assert rf_model.predict(features[:1])[0] in genres


def test_invalid_model_type():
    """Test error handling for invalid model types."""
    with pytest.raises(ValueError, match="Invalid model type"):
        GenreClassifier(model_type="invalid_model")._create_model()
