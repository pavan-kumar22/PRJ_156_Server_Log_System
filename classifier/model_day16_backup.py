"""Machine-learning model for log classification."""

from __future__ import annotations

import logging
from typing import Final

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


LOGGER = logging.getLogger(__name__)

CATEGORIES: Final[list[str]] = [
    "Routine Audit",
    "Performance Degradation",
    "Security Threat",
    "System Failure",
]


TRAINING_DATA: Final[list[tuple[str, str]]] = [
    (
        "User authentication successful",
        "Routine Audit",
    ),
    (
        "User session created successfully",
        "Routine Audit",
    ),
    (
        "Authentication token refreshed",
        "Routine Audit",
    ),
    (
        "Student application submitted successfully",
        "Routine Audit",
    ),
    (
        "Student profile retrieved successfully",
        "Routine Audit",
    ),
    (
        "Certificate information retrieved",
        "Routine Audit",
    ),
    (
        "Faculty verification completed successfully",
        "Routine Audit",
    ),
    (
        "Faculty application retrieved",
        "Routine Audit",
    ),
    (
        "Approval request submitted successfully",
        "Routine Audit",
    ),
    (
        "Approval request status retrieved",
        "Routine Audit",
    ),
    (
        "Document uploaded successfully",
        "Routine Audit",
    ),
    (
        "Document downloaded successfully",
        "Routine Audit",
    ),
    (
        "Payment transaction completed successfully",
        "Routine Audit",
    ),
    (
        "Payment status retrieved successfully",
        "Routine Audit",
    ),
    (
        "Student application retrieved successfully",
        "Routine Audit",
    ),
    (
        "Faculty profile retrieved successfully",
        "Routine Audit",
    ),
    (
        "Approval request processed successfully",
        "Routine Audit",
    ),
    (
        "Document verification completed successfully",
        "Routine Audit",
    ),
    (
        "Payment request processed successfully",
        "Routine Audit",
    ),
    (
        "User logout completed successfully",
        "Routine Audit",
    ),
    (
        "Student profile request exceeded latency threshold",
        "Performance Degradation",
    ),
    (
        "Faculty verification processing is slow",
        "Performance Degradation",
    ),
    (
        "Approval workflow processing latency is high",
        "Performance Degradation",
    ),
    (
        "Payment gateway response latency is increasing",
        "Performance Degradation",
    ),
    (
        "Document upload processing is slow",
        "Performance Degradation",
    ),
    (
        "Payment gateway request timed out",
        "Performance Degradation",
    ),
    (
        "Faculty verification request timed out",
        "Performance Degradation",
    ),
    (
        "Student application request timed out",
        "Performance Degradation",
    ),
    (
        "Approval workflow request timed out",
        "Performance Degradation",
    ),
    (
        "Service response latency exceeded threshold",
        "Performance Degradation",
    ),
    (
        "API response time is increasing",
        "Performance Degradation",
    ),
    (
        "Database request latency is high",
        "Performance Degradation",
    ),
    (
        "Database query took too long to complete",
        "Performance Degradation",
    ),
    (
        "High latency detected in payment service",
        "Performance Degradation",
    ),
    (
        "API request timeout detected",
        "Performance Degradation",
    ),
    (
        "Database query response is very slow",
        "Performance Degradation",
    ),
    (
        "Payment service response latency is high",
        "Performance Degradation",
    ),
    (
        "API request took too long to respond",
        "Performance Degradation",
    ),
    (
        "Unauthorized administrative access attempt detected",
        "Security Threat",
    ),
    (
        "Unauthorized access attempt detected",
        "Security Threat",
    ),
    (
        "Suspicious repeated document access detected",
        "Security Threat",
    ),
    (
        "Potential fraudulent payment activity detected",
        "Security Threat",
    ),
    (
        "Access denied for protected student resource",
        "Security Threat",
    ),
    (
        "Brute force authentication attempt detected",
        "Security Threat",
    ),
    (
        "Suspicious payment activity detected",
        "Security Threat",
    ),
    (
        "Invalid authentication token detected",
        "Security Threat",
    ),
    (
        "Unauthorized document access detected",
        "Security Threat",
    ),
    (
        "Multiple failed login attempts detected",
        "Security Threat",
    ),
    (
        "Suspicious administrative activity detected",
        "Security Threat",
    ),
    (
        "Unauthorized faculty access detected",
        "Security Threat",
    ),
    (
        "Payment database connection failed",
        "System Failure",
    ),
    (
        "Faculty verification database connection failed",
        "System Failure",
    ),
    (
        "Student portal database connection failed",
        "System Failure",
    ),
    (
        "Document storage service failed",
        "System Failure",
    ),
    (
        "Authentication database connection failed",
        "System Failure",
    ),
    (
        "Approval workflow service unavailable",
        "System Failure",
    ),
    (
        "Payment service unavailable",
        "System Failure",
    ),
    (
        "Document storage connection failed",
        "System Failure",
    ),
    (
        "Authentication service failed",
        "System Failure",
    ),
    (
        "Database connection failure detected",
        "System Failure",
    ),
    (
        "Backend service crashed",
        "System Failure",
    ),
    (
        "Application server crashed unexpectedly",
        "System Failure",
    ),
    (
        "Critical system component failed",
        "System Failure",
    ),
]


class LogClassifier:
    """Train and expose a TF-IDF and LinearSVC log classifier."""

    def __init__(self) -> None:
        """Initialize and train the classification pipeline."""
        self.pipeline = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        lowercase=True,
                        strip_accents="unicode",
                        ngram_range=(1, 2),
                        sublinear_tf=True,
                    ),
                ),
                (
                    "classifier",
                    LinearSVC(
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
            ]
        )

        self._train()

    def _train(self) -> None:
        """Train the machine-learning pipeline."""
        messages = [item[0] for item in TRAINING_DATA]
        labels = [item[1] for item in TRAINING_DATA]

        self.pipeline.fit(messages, labels)

        LOGGER.info(
            "Log classification model trained successfully "
            "with %d training samples.",
            len(TRAINING_DATA),
        )

    def predict(self, message: str) -> tuple[str, float]:
        """
        Predict the category of a log message.

        Args:
            message: Log message to classify.

        Returns:
            Tuple containing predicted category and confidence score.
        """
        prediction = self.pipeline.predict([message])[0]

        decision_scores = self.pipeline.decision_function([message])[0]

        max_score = float(max(decision_scores))
        confidence = 1.0 / (1.0 + pow(2.718281828, -max_score))

        return prediction, round(confidence, 4)