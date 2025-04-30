#!/usr/bin/env python3
"""
Metaflow workflow for movie genre classification.

This workflow orchestrates the entire machine learning pipeline for
predicting movie genres based on plot summaries.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

import numpy as np
import pandas as pd
from metaflow import FlowSpec, step, Parameter, IncludeFile
from sklearn.metrics import accuracy_score, classification_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class GenreClassifierFlow(FlowSpec):
    """
    Metaflow workflow for movie genre classification.

    This workflow handles:
    1. Data loading and preprocessing
    2. Feature extraction using TF-IDF
    3. Model training (Logistic Regression)
    4. Model evaluation
    5. Model deployment
    """

    # Parameters
    data_path = Parameter(
        "data-path",
        help="Path to the processed data directory",
        default="./data/processed",
    )

    model_type = Parameter(
        "model-type",
        help="Type of model to train",
        default="logreg",
    )

    max_features = Parameter(
        "max-features",
        help="Maximum number of features for TF-IDF",
        default=10000,
    )

    test_size = Parameter(
        "test-size",
        help="Fraction of data to use for testing",
        default=0.2,
    )

    random_state = Parameter(
        "random-state",
        help="Random seed for reproducibility",
        default=42,
    )

    @step
    def start(self):
        """
        Start the workflow and validate parameters.
        """
        import os

        print(f"Starting movie genre classification workflow")
        print(f"Parameters:")
        print(f"  Data path: {self.data_path}")
        print(f"  Model type: {self.model_type}")
        print(f"  Max features: {self.max_features}")

        # Validate parameters
        if self.model_type not in ["logreg", "naive_bayes", "random_forest"]:
            raise ValueError(f"Invalid model type: {self.model_type}")

        # Check if data directory exists
        if not os.path.exists(self.data_path):
            raise ValueError(f"Data directory not found: {self.data_path}")

        # Continue to the next step
        self.next(self.load_data)

    @step
    def load_data(self):
        """
        Load and preprocess the movie data.
        """
        import pandas as pd
        import os

        print("Loading data...")

        # Load the processed datasets
        data_dir = Path(self.data_path)
        self.train_data = pd.read_csv(data_dir / "train.csv")
        self.val_data = pd.read_csv(data_dir / "validation.csv")
        self.test_data = pd.read_csv(data_dir / "test.csv")

        print(f"Loaded {len(self.train_data)} training samples")
        print(f"Loaded {len(self.val_data)} validation samples")
        print(f"Loaded {len(self.test_data)} test samples")

        # Print genre distribution
        print("\nTraining data genre distribution:")
        genre_counts = self.train_data["genre"].value_counts()
        for genre, count in genre_counts.items():
            print(f"  {genre}: {count} ({count/len(self.train_data):.2%})")

        # Continue to the next step
        self.next(self.extract_features)

    @step
    def extract_features(self):
        """
        Extract features from the plot summaries using TF-IDF.
        """
        from src.features.text_features import TextFeatureExtractor

        print("Extracting text features...")

        # Create a feature extractor
        self.feature_extractor = TextFeatureExtractor(
            max_features=self.max_features,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
        )

        # Extract features from the plot summaries
        X_train = self.feature_extractor.fit_transform_tfidf(self.train_data["plot"].tolist())
        X_val = self.feature_extractor.transform_tfidf(self.val_data["plot"].tolist())
        X_test = self.feature_extractor.transform_tfidf(self.test_data["plot"].tolist())

        # Store features for the next step
        self.X_train = X_train
        self.X_val = X_val
        self.X_test = X_test
        self.y_train = self.train_data["genre"].tolist()
        self.y_val = self.val_data["genre"].tolist()
        self.y_test = self.test_data["genre"].tolist()

        print(f"Extracted features with shape:")
        print(f"  Training: {self.X_train.shape}")
        print(f"  Validation: {self.X_val.shape}")
        print(f"  Test: {self.X_test.shape}")

        # Continue to the next step
        self.next(self.train_model)

    @step
    def train_model(self):
        """
        Train a machine learning model on the extracted features.
        """
        from src.model.train import train_model

        print(f"Training {self.model_type} model...")

        # Train the model
        self.model = train_model(
            X_train=self.X_train,
            y_train=self.y_train,
            model_type=self.model_type,
            model_params={},
        )

        print("Model training completed")

        # Continue to the next step
        self.next(self.evaluate_model)

    @step
    def evaluate_model(self):
        """
        Evaluate the trained model on test data.
        """
        from src.model.evaluate import evaluate_model

        print("Evaluating model performance...")

        # Evaluate on validation data
        self.val_metrics = evaluate_model(
            model=self.model,
            X_test=self.X_val,
            y_test=self.y_val,
        )

        # Evaluate on test data
        self.test_metrics = evaluate_model(
            model=self.model,
            X_test=self.X_test,
            y_test=self.y_test,
        )

        print(f"Validation accuracy: {self.val_metrics['accuracy']:.4f}")
        print(f"Test accuracy: {self.test_metrics['accuracy']:.4f}")

        # Find genres where the model performs worst
        report = self.test_metrics["per_class"]
        per_class_f1 = {genre: report[genre]["f1-score"] for genre in report if genre not in ["accuracy", "macro avg", "weighted avg"]}
        worst_genres = sorted(per_class_f1.items(), key=lambda x: x[1])[:3]

        print("\nWorst performing genres:")
        for genre, f1 in worst_genres:
            print(f"  {genre}: F1 = {f1:.4f}")

        # Continue to the next step
        self.next(self.save_model)

    @step
    def save_model(self):
        """
        Save the trained model and artifacts for deployment.
        """
        import os
        import joblib
        from datetime import datetime

        print("Saving model artifacts...")

        # Create models directory if it doesn't exist
        models_dir = Path("./models")
        models_dir.mkdir(exist_ok=True)

        # Generate a timestamp for the model version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = models_dir / f"{self.model_type}_{timestamp}"
        model_dir.mkdir(exist_ok=True)

        # Save the model
        model_path = model_dir / "genre_classifier.joblib"
        self.model.save(model_path)

        # Save the feature extractor
        feature_path = model_dir / "feature_extractor.joblib"
        self.feature_extractor.save(feature_path)

        # Save the model info and metrics
        info = {
            "model_type": self.model_type,
            "max_features": self.max_features,
            "timestamp": timestamp,
            "validation_metrics": self.val_metrics,
            "test_metrics": self.test_metrics,
            "genres": self.model.label_encoder.classes_.tolist(),
        }

        with open(model_dir / "model_info.json", "w") as f:
            json.dump(info, f, indent=2)

        # Store model paths for the next step
        self.model_dir = str(model_dir)
        self.model_path = str(model_path)
        self.feature_path = str(feature_path)

        print(f"Model artifacts saved to {model_dir}")

        # Continue to the next step
        self.next(self.end)

    @step
    def end(self):
        """
        End the workflow and print summary.
        """
        print("\nWorkflow completed successfully!")
        print(f"Model saved to: {self.model_path}")
        print(f"Feature extractor saved to: {self.feature_path}")
        print(f"Test accuracy: {self.test_metrics['accuracy']:.4f}")
        print(f"Test F1 score (weighted): {self.test_metrics['f1']:.4f}")

        # Print a reminder about how to deploy the model
        print("\nTo deploy the model as a FastAPI service:")
        print(f"  1. Set MODEL_PATH={self.model_path}")
        print(f"  2. Set FEATURE_EXTRACTOR_PATH={self.feature_path}")
        print(f"  3. Run: uvicorn src.api.main:app --reload")


if __name__ == "__main__":
    GenreClassifierFlow()
