#!/usr/bin/env python3
"""
API models for the movie genre predictor.

This module defines the Pydantic models used by the FastAPI application
for request and response validation.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """
    Request model for genre prediction.

    Attributes:
        plot: The movie plot summary text
    """

    plot: str = Field(..., min_length=10, description="Movie plot summary text")

    class Config:
        json_schema_extra = {
            "example": {
                "plot": "A computer hacker learns from mysterious rebels about the true nature "
                "of his reality and his role in the war against its controllers."
            }
        }


class GenrePrediction(BaseModel):
    """
    Single genre prediction with confidence score.

    Attributes:
        genre: Predicted genre name
        confidence: Confidence score for the prediction (0.0 to 1.0)
    """

    genre: str = Field(..., description="Predicted genre name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class PredictionResponse(BaseModel):
    """
    Response model for genre prediction.

    Attributes:
        predicted_genre: The top predicted genre
        confidence: Confidence score for the prediction
        all_predictions: List of all genre predictions with confidence scores
        plot_summary: The original plot summary used for prediction
    """

    predicted_genre: str = Field(..., description="Top predicted genre")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for top genre")
    all_predictions: List[GenrePrediction] = Field(
        ..., description="All genre predictions with confidence scores"
    )
    plot_summary: str = Field(..., description="Original plot summary used for prediction")


class ModelInfo(BaseModel):
    """
    Information about the currently loaded model.

    Attributes:
        model_type: Type of model (e.g., "logreg", "naive_bayes")
        num_genres: Number of genres the model can predict
        available_genres: List of available genres
        model_version: Model version or timestamp
        feature_extractor_info: Information about the feature extractor
    """

    model_type: str = Field(..., description="Type of model used")
    num_genres: int = Field(..., description="Number of genres the model can predict")
    available_genres: List[str] = Field(..., description="List of available genres")
    model_version: str = Field(..., description="Model version or timestamp")
    feature_extractor_info: Dict[str, Any] = Field(
        ..., description="Information about the feature extractor"
    )


class HealthResponse(BaseModel):
    """
    Response model for the health check endpoint.

    Attributes:
        status: Service status (e.g., "ok", "degraded")
        model_loaded: Whether a model is loaded
        api_version: API version
    """

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether a model is loaded")
    api_version: str = Field(..., description="API version")
