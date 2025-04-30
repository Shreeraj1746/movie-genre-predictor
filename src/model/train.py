#!/usr/bin/env python3
"""
Model training module for movie genre prediction.

This module provides functions to train and save machine learning
models for predicting movie genres based on plot summaries.
"""

import logging
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
ROOT_DIR = Path(__file__).resolve().parents[2]  # project root directory
MODELS_DIR = ROOT_DIR / "models"


class GenreClassifier:
    """
    Classifier for movie genres based on textual features.

    This class provides methods to train, evaluate, and save/load a genre
    classification model based on text features from plot summaries.
    """

    def __init__(
        self,
        model_type: str = "logreg",
        model_params: dict[str, Any] | None = None,
    ):
        """
        Initialize a GenreClassifier.

        Args:
            model_type: Type of model to use (one of: "logreg", "naive_bayes",
                "random_forest", "svm")
            model_params: Parameters for the model. If None, default parameters
                are used.
        """
        self.model_type = model_type
        self.model_params = model_params or {}
        self.model = None
        self.label_encoder = LabelEncoder()

    def _create_model(self) -> Any:
        """
        Create a new classification model based on model_type.

        Returns:
            A scikit-learn classifier instance

        Raises:
            ValueError: If the model type is invalid
        """
        logger.info(f"Creating {self.model_type} model")

        if self.model_type == "logreg":
            model = LogisticRegression(
                C=self.model_params.get("C", 1.0),
                max_iter=self.model_params.get("max_iter", 1000),
                solver=self.model_params.get("solver", "lbfgs"),
                n_jobs=self.model_params.get("n_jobs", -1),
                random_state=self.model_params.get("random_state", 42),
            )
        elif self.model_type == "naive_bayes":
            model = MultinomialNB(
                alpha=self.model_params.get("alpha", 1.0),
                fit_prior=self.model_params.get("fit_prior", True),
            )
        elif self.model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=self.model_params.get("n_estimators", 100),
                max_depth=self.model_params.get("max_depth", None),
                min_samples_split=self.model_params.get("min_samples_split", 2),
                random_state=self.model_params.get("random_state", 42),
                n_jobs=self.model_params.get("n_jobs", -1),
            )
        elif self.model_type == "svm":
            model = SVC(
                C=self.model_params.get("C", 1.0),
                kernel=self.model_params.get("kernel", "linear"),
                probability=True,
                random_state=self.model_params.get("random_state", 42),
            )
        else:
            raise ValueError(f"Invalid model type: {self.model_type}")

        return model

    def fit(
        self,
        features_train: np.ndarray,
        y_train: np.ndarray,
        classes: list[str] | None = None,
    ) -> "GenreClassifier":
        """
        Fit the model on the training data.

        Args:
            features_train: Training features
            y_train: Training labels (genre strings)
            classes: Optional list of class labels

        Returns:
            Self, for method chaining

        Raises:
            ValueError: If training fails
        """
        if len(y_train) == 0:
            raise ValueError("No training data provided")

        # Fit the label encoder
        if classes is not None:
            self.label_encoder = LabelEncoder().fit(classes)
        else:
            self.label_encoder = LabelEncoder().fit(y_train)

        # Encode the training labels
        y_train_encoded = self.label_encoder.transform(y_train)

        # Create and train the model
        self.model = self._create_model()
        self.model.fit(features_train, y_train_encoded)

        logger.info(
            f"Trained model on {len(y_train)} examples with "
            f"{len(self.label_encoder.classes_)} classes"
        )
        return self

    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Predict the genre for the given features.

        Args:
            features: Feature matrix

        Returns:
            Array of predicted genre labels

        Raises:
            ValueError: If the model has not been trained
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")

        y_pred_encoded = self.model.predict(features)
        return self.label_encoder.inverse_transform(y_pred_encoded)

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """
        Predict genre probabilities for the given features.

        Args:
            features: Feature matrix

        Returns:
            Array of predicted probabilities for each genre

        Raises:
            ValueError: If the model has not been trained or does not
                support predict_proba
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")

        if not hasattr(self.model, "predict_proba"):
            raise ValueError(
                f"{self.model_type} does not support probability predictions"
            )

        return self.model.predict_proba(features)

    def evaluate(self, features_test: np.ndarray, y_test: np.ndarray) -> dict[str, Any]:
        """
        Evaluate the model on test data.

        Args:
            features_test: Test features
            y_test: Test labels (genre strings)

        Returns:
            Dictionary of evaluation metrics

        Raises:
            ValueError: If the model has not been trained
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")

        # Generate predictions
        y_pred_encoded = self.model.predict(features_test)
        y_pred = self.label_encoder.inverse_transform(y_pred_encoded)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average="macro")
        weighted_f1 = f1_score(y_test, y_pred, average="weighted")

        logger.info(f"Model evaluation on {len(y_test)} test examples:")
        logger.info(f"  Accuracy: {accuracy:.4f}")
        logger.info(f"  Macro F1: {macro_f1:.4f}")
        logger.info(f"  Weighted F1: {weighted_f1:.4f}")

        # Get per-class metrics
        report = classification_report(y_test, y_pred, output_dict=True)

        return {
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "weighted_f1": weighted_f1,
            "classification_report": report,
        }

    def save(self, filepath: Path) -> None:
        """
        Save the trained model to a file.

        Args:
            filepath: Path to save the model to

        Raises:
            ValueError: If the model has not been trained
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")

        os.makedirs(filepath.parent, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "label_encoder": self.label_encoder,
                "model_type": self.model_type,
                "model_params": self.model_params,
            },
            filepath,
        )

        logger.info(f"Saved model to {filepath}")

    @classmethod
    def load(cls, filepath: Path) -> "GenreClassifier":
        """
        Load a trained model from a file.

        Args:
            filepath: Path to load the model from

        Returns:
            Loaded GenreClassifier instance
        """
        logger.info(f"Loading model from {filepath}")

        data = joblib.load(filepath)

        classifier = cls(
            model_type=data["model_type"],
            model_params=data["model_params"],
        )
        classifier.model = data["model"]
        classifier.label_encoder = data["label_encoder"]

        return classifier


def train_model(
    features_train: np.ndarray,
    y_train: np.ndarray,
    model_type: str = "logreg",
    model_params: dict[str, Any] | None = None,
    model_path: Path | None = None,
) -> GenreClassifier:
    """
    Train a genre classification model.

    Args:
        features_train: Training features
        y_train: Training labels (genre strings)
        model_type: Type of model to use
        model_params: Parameters for the model
        model_path: Path to save the trained model. If None, the model is not saved.

    Returns:
        Trained GenreClassifier instance
    """
    # Create and train the classifier
    classifier = GenreClassifier(model_type=model_type, model_params=model_params)
    classifier.fit(features_train, y_train)

    # Save the model if a path is provided
    if model_path is not None:
        classifier.save(model_path)

    return classifier


if __name__ == "__main__":
    # Example usage
    from sklearn.datasets import fetch_20newsgroups
    from sklearn.feature_extraction.text import TfidfVectorizer

    # Load a text classification dataset as an example
    categories = ["alt.atheism", "sci.space", "rec.sport.baseball"]
    newsgroups = fetch_20newsgroups(categories=categories, subset="train")

    # Extract features
    vectorizer = TfidfVectorizer(max_features=1000)
    features = vectorizer.fit_transform(newsgroups.data)
    y = np.array(newsgroups.target_names)[newsgroups.target]

    # Train model
    model = train_model(features, y, model_type="logreg")

    # Print some example predictions
    texts = [
        "The spacecraft is scheduled to launch next week.",
        "The team won the championship after a close game.",
        "The debate about religion continues with no clear conclusion.",
    ]
    X_new = vectorizer.transform(texts)
    predictions = model.predict(X_new)

    for text, pred in zip(texts, predictions, strict=False):
        print(f"Text: {text[:30]}... -> Prediction: {pred}")
