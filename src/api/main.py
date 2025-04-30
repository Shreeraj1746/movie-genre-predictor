#!/usr/bin/env python3
"""
FastAPI application for the movie genre predictor.

This module provides a REST API for predicting movie genres based on plot summaries
using a trained machine learning model.
"""

import os
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.api.models import (
    PredictionRequest,
    PredictionResponse,
    GenrePrediction,
    ModelInfo,
    HealthResponse,
)
from src.model.train import GenreClassifier
from src.features.text_features import TextFeatureExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
APP_VERSION = "0.1.0"

# Create FastAPI app
app = FastAPI(
    title="Movie Genre Predictor API",
    description="API for predicting movie genres based on plot summaries",
    version=APP_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global variables for model and feature extractor
model = None
feature_extractor = None


def get_model_path() -> Optional[str]:
    """Get the model path from environment variable or default location."""
    return os.environ.get("MODEL_PATH", None)


def get_feature_extractor_path() -> Optional[str]:
    """Get the feature extractor path from environment variable or default location."""
    return os.environ.get("FEATURE_EXTRACTOR_PATH", None)


def load_model() -> Tuple[Optional[GenreClassifier], Optional[TextFeatureExtractor]]:
    """
    Load the model and feature extractor from disk.

    Returns:
        Tuple of (model, feature_extractor)
    """
    global model, feature_extractor

    model_path = get_model_path()
    feature_extractor_path = get_feature_extractor_path()

    if model_path and os.path.exists(model_path):
        try:
            logger.info(f"Loading model from {model_path}")
            model = GenreClassifier.load(Path(model_path))
            logger.info(f"Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            model = None

    if feature_extractor_path and os.path.exists(feature_extractor_path):
        try:
            logger.info(f"Loading feature extractor from {feature_extractor_path}")
            feature_extractor = TextFeatureExtractor.load(Path(feature_extractor_path))
            logger.info(f"Feature extractor loaded successfully")
        except Exception as e:
            logger.error(f"Error loading feature extractor: {e}")
            feature_extractor = None

    return model, feature_extractor


# Load model and feature extractor on startup
@app.on_event("startup")
async def startup_event():
    """Load the model and feature extractor on startup."""
    global model, feature_extractor
    model, feature_extractor = load_model()


@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint that returns basic API information."""
    return {
        "message": "Welcome to the Movie Genre Predictor API",
        "version": APP_VERSION,
        "docs_url": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint that returns the status of the API.

    Returns:
        HealthResponse: API health status
    """
    global model, feature_extractor

    model_loaded = model is not None and feature_extractor is not None

    if not model_loaded:
        # Try to load the model if not already loaded
        model, feature_extractor = load_model()
        model_loaded = model is not None and feature_extractor is not None

    status = "ok" if model_loaded else "degraded"

    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        api_version=APP_VERSION,
    )


@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
async def get_model_info():
    """
    Get information about the currently loaded model.

    Returns:
        ModelInfo: Information about the model

    Raises:
        HTTPException: If the model is not loaded
    """
    global model, feature_extractor

    if model is None or feature_extractor is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please ensure the model paths are configured correctly.",
        )

    # Get the model directory from the model path
    model_path = get_model_path()
    model_dir = os.path.dirname(model_path) if model_path else "unknown"

    # Extract the model version from the directory name (e.g., "logreg_20230101_123456")
    model_version = os.path.basename(model_dir) if model_dir != "unknown" else "unknown"

    # Get the list of available genres
    available_genres = model.label_encoder.classes_.tolist()

    # Get feature extractor info
    feature_extractor_info = {
        "max_features": feature_extractor.max_features,
        "ngram_range": feature_extractor.ngram_range,
        "min_df": feature_extractor.min_df,
        "max_df": feature_extractor.max_df,
    }

    return ModelInfo(
        model_type=model.model_type,
        num_genres=len(available_genres),
        available_genres=available_genres,
        model_version=model_version,
        feature_extractor_info=feature_extractor_info,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_genre(request: PredictionRequest):
    """
    Predict the genre of a movie based on its plot summary.

    Args:
        request: PredictionRequest containing the plot summary

    Returns:
        PredictionResponse: Predicted genre and confidence scores

    Raises:
        HTTPException: If the model is not loaded or prediction fails
    """
    global model, feature_extractor

    if model is None or feature_extractor is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please ensure the model paths are configured correctly.",
        )

    try:
        # Preprocess the plot summary
        plot = request.plot

        # Extract features
        X = feature_extractor.transform_tfidf([plot])

        # Make prediction
        predicted_genre = model.predict(X)[0]

        # Get prediction probabilities
        if hasattr(model.model, "predict_proba"):
            probs = model.predict_proba(X)[0]
            genre_indices = np.argsort(probs)[::-1]  # Sort in descending order
            genres = model.label_encoder.classes_[genre_indices]
            confidences = probs[genre_indices]

            # Get confidence for the top prediction
            top_confidence = confidences[0]

            # Create prediction response
            all_predictions = [
                GenrePrediction(genre=genre, confidence=float(conf))
                for genre, conf in zip(genres, confidences)
            ]
        else:
            # If the model doesn't support probabilities, use a default confidence of 1.0
            top_confidence = 1.0
            all_predictions = [GenrePrediction(genre=predicted_genre, confidence=1.0)]

        return PredictionResponse(
            predicted_genre=predicted_genre,
            confidence=float(top_confidence),
            all_predictions=all_predictions,
            plot_summary=plot,
        )

    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error making prediction: {str(e)}",
        )


if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
