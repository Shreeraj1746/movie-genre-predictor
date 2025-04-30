#!/usr/bin/env python3
"""
Tests for the FastAPI application.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.features.text_features import TextFeatureExtractor
from src.model.train import GenreClassifier


@pytest.fixture()
def test_client():
    """Create a test client for the FastAPI app."""
    client = TestClient(app)
    return client


@pytest.fixture()
def mock_model():
    """Create a mock model for testing."""
    model = MagicMock(spec=GenreClassifier)
    model.model_type = "logreg"
    model.label_encoder = MagicMock()
    model.label_encoder.classes_ = np.array(["action", "comedy", "drama"])
    model.predict.return_value = np.array(["action"])
    model.predict_proba.return_value = np.array([[0.7, 0.2, 0.1]])
    model.model = MagicMock()
    model.model.predict_proba = MagicMock()
    return model


@pytest.fixture()
def mock_feature_extractor():
    """Create a mock feature extractor for testing."""
    extractor = MagicMock(spec=TextFeatureExtractor)
    extractor.max_features = 1000
    extractor.ngram_range = (1, 2)
    extractor.min_df = 2
    extractor.max_df = 0.95
    extractor.transform_tfidf.return_value = np.array([[0.1, 0.2, 0.3]])
    return extractor


def test_root_endpoint(test_client):
    """Test the root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Movie Genre Predictor API" in response.json()["message"]


def test_health_endpoint_no_model(test_client):
    """Test the health endpoint when no model is loaded."""
    with patch("src.api.main.model", None), patch(
        "src.api.main.feature_extractor", None
    ), patch("src.api.main.load_model", return_value=(None, None)):
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "degraded"
        assert not response.json()["model_loaded"]


def test_health_endpoint_with_model(test_client, mock_model, mock_feature_extractor):
    """Test the health endpoint when a model is loaded."""
    with patch("src.api.main.model", mock_model), patch(
        "src.api.main.feature_extractor", mock_feature_extractor
    ):
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["model_loaded"]


def test_model_info_endpoint(test_client, mock_model, mock_feature_extractor):
    """Test the model info endpoint."""
    with patch("src.api.main.model", mock_model), patch(
        "src.api.main.feature_extractor", mock_feature_extractor
    ), patch(
        "src.api.main.get_model_path",
        return_value="/path/to/logreg_20230101_123456/model.joblib",
    ):
        response = test_client.get("/model/info")
        assert response.status_code == 200
        assert response.json()["model_type"] == "logreg"
        assert response.json()["num_genres"] == 3
        assert response.json()["model_version"] == "logreg_20230101_123456"


def test_predict_endpoint(test_client, mock_model, mock_feature_extractor):
    """Test the prediction endpoint."""
    with patch("src.api.main.model", mock_model), patch(
        "src.api.main.feature_extractor", mock_feature_extractor
    ):
        response = test_client.post(
            "/predict",
            json={"plot": "A thrilling action movie about a spy on a mission."},
        )
        assert response.status_code == 200
        assert response.json()["predicted_genre"] == "action"
        assert response.json()["confidence"] == 0.7
        assert len(response.json()["all_predictions"]) == 3


def test_predict_endpoint_no_model(test_client):
    """Test the prediction endpoint when no model is loaded."""
    with patch("src.api.main.model", None), patch(
        "src.api.main.feature_extractor", None
    ):
        response = test_client.post(
            "/predict",
            json={"plot": "A thrilling action movie about a spy on a mission."},
        )
        assert response.status_code == 503
        assert "Model not loaded" in response.json()["detail"]


def test_prediction_validation(test_client, mock_model, mock_feature_extractor):
    """Test validation of prediction requests."""
    with patch("src.api.main.model", mock_model), patch(
        "src.api.main.feature_extractor", mock_feature_extractor
    ):
        # Test with empty plot
        response = test_client.post("/predict", json={"plot": ""})
        assert response.status_code == 422

        # Test with missing plot
        response = test_client.post("/predict", json={})
        assert response.status_code == 422

        # Test with plot that's too short
        response = test_client.post("/predict", json={"plot": "Short"})
        assert response.status_code == 422
