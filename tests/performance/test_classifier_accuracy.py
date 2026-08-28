"""
Formal ML classifier accuracy evaluation.

Evaluation method:
- Uses the project's existing labelled TRAINING_DATA.
- Creates a stratified 80/20 train-test split.
- Trains an independent TF-IDF + LinearSVC pipeline.
- Evaluates only on the held-out test set.
- Reports accuracy, precision, recall, F1-score,
  per-class performance, and confusion matrix.

This script does not modify the production classifier.
"""

from pathlib import Path
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from classifier.model import TRAINING_DATA


# ============================================================
# CONFIGURATION
# ============================================================

TEST_SIZE = 0.20
RANDOM_STATE = 42

MINIMUM_ACCEPTABLE_ACCURACY = 0.90
OPTIMIZATION_TARGET_ACCURACY = 0.965


# ============================================================
# LOAD DATA
# ============================================================

messages = [item[0] for item in TRAINING_DATA]
labels = [item[1] for item in TRAINING_DATA]

print()
print("=" * 75)
print("AICTE SERVER LOG MONITORING SYSTEM")
print("FORMAL ML CLASSIFIER ACCURACY EVALUATION")
print("=" * 75)

print(f"Total labelled samples : {len(messages)}")
print(f"Test split             : {TEST_SIZE * 100:.0f}%")
print(f"Random state            : {RANDOM_STATE}")


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    messages,
    labels,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=labels,
)

print(f"Training samples       : {len(X_train)}")
print(f"Held-out test samples  : {len(X_test)}")


# ============================================================
# INDEPENDENT EVALUATION MODEL
# ============================================================

evaluation_pipeline = Pipeline(
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


# ============================================================
# TRAIN
# ============================================================

print()
print("Training evaluation model...")

evaluation_pipeline.fit(X_train, y_train)

print("Training completed.")


# ============================================================
# PREDICTION
# ============================================================

y_pred = evaluation_pipeline.predict(X_test)


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(y_test, y_pred)

report = classification_report(
    y_test,
    y_pred,
    output_dict=True,
    zero_division=0,
)

precision = report["weighted avg"]["precision"]
recall = report["weighted avg"]["recall"]
f1 = report["weighted avg"]["f1-score"]

matrix = confusion_matrix(
    y_test,
    y_pred,
    labels=sorted(set(labels)),
)

categories = sorted(set(labels))


# ============================================================
# RESULTS
# ============================================================

print()
print("=" * 75)
print("FORMAL EVALUATION RESULTS")
print("=" * 75)

print(f"Accuracy              : {accuracy * 100:.2f}%")
print(f"Weighted Precision    : {precision * 100:.2f}%")
print(f"Weighted Recall       : {recall * 100:.2f}%")
print(f"Weighted F1-score     : {f1 * 100:.2f}%")

print()
print("Acceptance baseline  : 90.00%")
print("Optimization target   : 96.50%")

if accuracy >= MINIMUM_ACCEPTABLE_ACCURACY:
    print("Acceptance status     : PASS")
else:
    print("Acceptance status     : FAIL")

if accuracy >= OPTIMIZATION_TARGET_ACCURACY:
    print("Optimization status   : TARGET ACHIEVED")
else:
    print("Optimization status   : BELOW OPTIMIZATION TARGET")


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print()
print("=" * 75)
print("PER-CLASS CLASSIFICATION REPORT")
print("=" * 75)

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0,
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print()
print("=" * 75)
print("CONFUSION MATRIX")
print("=" * 75)

print("Labels:")
for index, category in enumerate(categories):
    print(f"{index}: {category}")

print()
print(matrix)


# ============================================================
# INDIVIDUAL TEST RESULTS
# ============================================================

print()
print("=" * 75)
print("HELD-OUT TEST CASE RESULTS")
print("=" * 75)

for message, expected, predicted in zip(
    X_test,
    y_test,
    y_pred,
):
    status = "PASS" if expected == predicted else "FAIL"

    print()
    print(f"[{status}]")
    print(f"Message   : {message}")
    print(f"Expected  : {expected}")
    print(f"Predicted : {predicted}")


# ============================================================
# SAVE RESULTS
# ============================================================

results_dir = Path("performance_results")
results_dir.mkdir(exist_ok=True)

results = {
    "test": "ML Classifier Accuracy",
    "model": "TF-IDF + LinearSVC",
    "total_samples": len(messages),
    "training_samples": len(X_train),
    "held_out_test_samples": len(X_test),
    "test_size": TEST_SIZE,
    "random_state": RANDOM_STATE,
    "accuracy": round(accuracy, 4),
    "accuracy_percent": round(accuracy * 100, 2),
    "weighted_precision": round(precision, 4),
    "weighted_recall": round(recall, 4),
    "weighted_f1": round(f1, 4),
    "minimum_acceptable_accuracy": MINIMUM_ACCEPTABLE_ACCURACY,
    "optimization_target_accuracy": OPTIMIZATION_TARGET_ACCURACY,
    "acceptance_status": (
        "PASS"
        if accuracy >= MINIMUM_ACCEPTABLE_ACCURACY
        else "FAIL"
    ),
    "optimization_status": (
        "TARGET ACHIEVED"
        if accuracy >= OPTIMIZATION_TARGET_ACCURACY
        else "BELOW OPTIMIZATION TARGET"
    ),
    "categories": categories,
    "confusion_matrix": matrix.tolist(),
}


output_file = results_dir / "classifier_accuracy.json"

with output_file.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        results,
        file,
        indent=2,
    )

print()
print("=" * 75)
print(f"Results saved to: {output_file}")
print("=" * 75)