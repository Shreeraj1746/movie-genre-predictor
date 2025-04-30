#!/usr/bin/env python3
"""
Model evaluation module for movie genre prediction.

This module provides functions to evaluate trained machine learning models
for predicting movie genres based on plot summaries.
"""

import json
import logging
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, precision_recall_fscore_support)

from src.model.train import GenreClassifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
ROOT_DIR = Path(__file__).resolve().parents[2]  # project root directory
REPORTS_DIR = ROOT_DIR / "reports"


def evaluate_model(
    model: GenreClassifier,
    features_test: np.ndarray,
    y_test: np.ndarray,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Evaluate a trained genre classification model.

    Args:
        model: Trained GenreClassifier instance
        features_test: Test features
        y_test: Test labels (genre strings)
        output_dir: Directory to save evaluation reports and visualizations.
            If None, reports are not saved.

    Returns:
        Dictionary of evaluation metrics
    """
    logger.info("Evaluating model performance")

    # Generate predictions
    y_pred = model.predict(features_test)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, average="weighted"
    )

    report_dict = classification_report(y_test, y_pred, output_dict=True)

    metrics = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "per_class": report_dict,
    }

    logger.info(f"Model accuracy: {accuracy:.4f}")
    logger.info(f"Model F1 score (weighted): {f1:.4f}")

    # Save reports if output_dir is provided
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save metrics to JSON file
        metrics_file = output_dir / "evaluation_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

        # Generate and save confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=model.label_encoder.classes_)
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=model.label_encoder.classes_,
            yticklabels=model.label_encoder.classes_,
        )
        plt.xlabel("Predicted Genre")
        plt.ylabel("True Genre")
        plt.title("Confusion Matrix")
        plt.tight_layout()
        plt.savefig(output_dir / "confusion_matrix.png")

        # Generate class distribution plot
        plt.figure(figsize=(12, 6))
        genre_counts = pd.Series(y_test).value_counts()
        sns.barplot(x=genre_counts.index, y=genre_counts.values)
        plt.xlabel("Genre")
        plt.ylabel("Count")
        plt.title("Test Data Genre Distribution")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(output_dir / "genre_distribution.png")

        logger.info(f"Saved evaluation reports to {output_dir}")

    return metrics


def evaluate_model_with_probability_threshold(
    model: GenreClassifier,
    features_test: np.ndarray,
    y_test: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """
    Evaluate a model using a custom probability threshold for classification.

    Args:
        model: Trained GenreClassifier instance
        features_test: Test features
        y_test: Test labels (genre strings)
        threshold: Probability threshold for classification

    Returns:
        Dictionary of evaluation metrics

    Raises:
        ValueError: If the model does not support probability predictions
    """
    if not hasattr(model.model, "predict_proba"):
        raise ValueError(f"{model.model_type} does not support probability predictions")

    logger.info(f"Evaluating model with probability threshold: {threshold}")

    # Get predicted probabilities
    y_proba = model.predict_proba(features_test)

    # Apply threshold to probabilities
    y_pred_one_hot = (y_proba >= threshold).astype(int)

    # For each sample, if no class is above threshold,
    # choose the highest probability class
    zero_pred_rows = y_pred_one_hot.sum(axis=1) == 0
    if np.any(zero_pred_rows):
        for i in np.where(zero_pred_rows)[0]:
            y_pred_one_hot[i, np.argmax(y_proba[i])] = 1

    # Convert back to class labels
    y_pred_encoded = np.argmax(y_pred_one_hot, axis=1)
    y_pred = model.label_encoder.inverse_transform(y_pred_encoded)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="weighted"
    )

    metrics = {
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

    logger.info(f"Metrics with threshold {threshold}:")
    logger.info(f"  Accuracy: {accuracy:.4f}")
    logger.info(f"  F1 Score: {f1:.4f}")

    return metrics


def find_optimal_threshold(
    model: GenreClassifier,
    features_val: np.ndarray,
    y_val: np.ndarray,
    thresholds: list[float] = None,
) -> tuple[float, dict[str, Any]]:
    """
    Find the optimal probability threshold for classification.

    Args:
        model: Trained GenreClassifier instance
        features_val: Validation features
        y_val: Validation labels (genre strings)
        thresholds: List of thresholds to evaluate. If None, defaults to
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    Returns:
        Tuple of (optimal_threshold, metrics_at_optimal_threshold)
    """
    if thresholds is None:
        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    logger.info("Finding optimal probability threshold")

    # Evaluate each threshold
    results = []
    for threshold in thresholds:
        metrics = evaluate_model_with_probability_threshold(
            model, features_val, y_val, threshold
        )
        results.append(metrics)

    # Find the threshold with the highest F1 score
    best_idx = max(range(len(results)), key=lambda i: results[i]["f1"])
    best_threshold = thresholds[best_idx]
    best_metrics = results[best_idx]

    logger.info(f"Optimal threshold: {best_threshold}")
    logger.info("Metrics at optimal threshold:")
    logger.info(f"  Accuracy: {best_metrics['accuracy']:.4f}")
    logger.info(f"  F1 Score: {best_metrics['f1']:.4f}")

    return best_threshold, best_metrics


if __name__ == "__main__":
    # Example usage
    from sklearn.datasets import fetch_20newsgroups
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import train_test_split

    from src.model.train import train_model

    # Load example dataset
    categories = ["alt.atheism", "sci.space", "rec.sport.baseball"]
    newsgroups = fetch_20newsgroups(categories=categories)

    # Extract features
    vectorizer = TfidfVectorizer(max_features=1000)
    features = vectorizer.fit_transform(newsgroups.data)
    y = np.array(newsgroups.target_names)[newsgroups.target]

    # Split data
    features_train, features_test, y_train, y_test = train_test_split(
        features, y, test_size=0.2, random_state=42
    )

    # Train model
    model = train_model(features_train, y_train, model_type="logreg")

    # Evaluate model
    metrics = evaluate_model(model, features_test, y_test)

    print(f"Test accuracy: {metrics['accuracy']:.4f}")
    print(f"Test F1 score: {metrics['f1']:.4f}")
